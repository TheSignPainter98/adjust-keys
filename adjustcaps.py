# Copyright (C) Edward Jones
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

from importlib.util import find_spec
blender_available:bool = find_spec('bpy') is not None

from adjustcaps_args import parse_args
from argparse import Namespace
if  blender_available:
    from bpy import ops
from concurrent.futures import ThreadPoolExecutor, wait
from copy import deepcopy
from functools import reduce
from layout import parse_layout
from log import init_logging, printi
from math import inf
from multiprocessing import cpu_count
from obj_io import read_obj, write_obj
from os import makedirs, walk
from os.path import basename, exists, join
from positions import resolve_cap_position, translate_to_origin
from util import concat, dict_union, flatten_list, inner_join, rem
from sys import argv, exit
from yaml_io import read_yaml


def main(*args: [[str]]) -> int:
    # Handle arguments; accept string, list of strings and list of lists of strings
    if all(map(lambda a: type(a) == str, args)):
        args = list(reduce(concat, map(lambda a: a.split(' '), args)))
    args = flatten_list(args)
    if type(args) == tuple:
        args = list(args)
    # Put executable name on the front if it is absent (e.g. if called from python with only the arguments specified)
    if args[0] != argv[0]:
        args = [argv[0]] + list(args)

    pargs: Namespace = parse_args(args)
    init_logging(pargs.verbosity)
    if pargs.move_to_origin:
        caps: [dict] = get_caps(pargs.cap_dir)
        if not exists(pargs.output_dir):
            printi('Making non-existent directory "%s"' % pargs.output_dir)
            makedirs(pargs.output_dir, exist_ok=True)
        for cap in caps:
            translate_to_origin(cap['cap-obj'])
            write_obj(join(pargs.output_dir, cap['cap-name'] + '.obj'), cap['cap-obj'])
    else:
        if not exists(pargs.output_dir):
            printi('Making non-existent directory "%s"' % pargs.output_dir)
            makedirs(pargs.output_dir, exist_ok=True)
        adjust_caps(pargs.unit_length, pargs.x_offset, pargs.y_offset,
                    pargs.plane, pargs.profile_file, pargs.cap_dir,
                    pargs.output_dir, pargs.layout_file,
                    pargs.layout_row_profile_file)

        #  seens:dict = {}
        #  for n,m in models:
        #  if n not in seens.keys():
        #  seens[n] = 1
        #  else:
        #  seens[n] += 1
        #  oname:str = join(pargs.output_dir, 'capmodel-' + n + ('-' + str(seens[n]) if seens[n] > 1 else '') + '.obj')
        #  printi('Outputting to "%s"' % oname)
        #  write_obj(oname, m)
        #  print(mfnames)
        #  for mfname in mfnames:
        #  bpy.ops.import_scene.obj(filepath=mfname)

    return 0


def adjust_caps(unit_length: float, x_offset: float, y_offset: float,
                plane: str, profile_file: str, cap_dir: str, output_dir: str,
                layout_file: str, layout_row_profile_file: str):
    printi('Reading layout information')
    layout_row_profiles: [str] = read_yaml(layout_row_profile_file)
    layout: [dict] = list(
        map(add_cap_name,
            parse_layout(layout_row_profiles, read_yaml(layout_file))))

    printi('Finding and parsing cap models')
    caps: [dict] = get_caps(cap_dir)
    layout_with_caps: [dict] = inner_join(caps, 'cap-name', layout, 'cap-name')

    # Resolve output unique output name
    seen: dict = {}
    printi('Resolving cap output names')
    for cap in layout_with_caps:
        if cap['cap-name'] not in seen:
            seen[cap['cap-name']] = 1
        else:
            seen[cap['cap-name']] += 1
        cap['oname'] = join(
            output_dir, 'capmodel-' + cap['cap-name'] +
            ('-' +
             str(seen[cap['cap-name']]) if seen[cap['cap-name']] > 1 else '') +
            '.obj')

    nprocs: int = 2 * cpu_count()
    printi('Adjusting and outputting caps on %d threads...' % nprocs)
    with ThreadPoolExecutor(nprocs) as ex:
        cops: ['[dict,str]->()'] = [
            ex.submit(handle_cap, cap, unit_length, x_offset, y_offset, plane)
            for cap in layout_with_caps
        ]
        wait(cops)

    # Sequentially import the models (for thread-safety)
    for cap in layout_with_caps:
        if blender_available:
            printi('Importing "%s" into blender...' % cap['oname'])
            ops.import_scene.obj(filepath=cap['oname'])


def de_spookify(cap: dict) -> dict:
    return dict_union(rem(cap, 'cap-obj'),
                      {'cap-obj': deepcopy(cap['cap-obj'])})


def handle_cap(cap: dict, unit_length: float, x_offset: float, y_offset: float,
               plane: str):
    printi('Adjusting cap %s' % cap['cap-name'])
    cap = de_spookify(cap)
    translate_to_origin(cap['cap-obj'], plane)
    cap = resolve_cap_position(cap, unit_length, x_offset, y_offset, plane)
    cap = apply_cap_position(cap)
    printi('Outputting to "%s"' % cap['oname'])
    write_obj(cap['oname'], cap['cap-obj'])


def apply_cap_position(cap: dict) -> dict:
    pos_x: float = cap['pos-x']
    pos_y: float = cap['pos-y']
    pos_z: float = cap['pos-z']
    for _, _, _, gd in cap['cap-obj']:
        for t, d in gd:
            if t == 'v':
                d[0] += pos_x
                d[1] += pos_y
                d[2] += pos_z
    return cap


def add_cap_name(key: dict) -> dict:
    key['cap-name'] = key['key-type'] if 'key-type' in key else (
        key['profile-part'] + '-' + str(key['width']).replace('.', '_') + 'u')
    return key


def get_caps(cap_dir: str) -> [dict]:
    capFiles: [str] = []
    for (root, _, fnames) in walk(cap_dir):
        capFiles += list(
            map(lambda f: join(root, f),
                list(filter(lambda f: f.endswith('.obj'), fnames))))
    return list(
        map(lambda c: {
            'cap-name': basename(c)[:-4],
            'cap-obj': read_obj(c)
        }, capFiles))


def gen_cap_file_name(cap_loc: str, cap: dict) -> str:
    return (join(cap_loc, cap['profile-part'] + '_' + cap['width'])
            if 'key-type' not in cap else cap['key-type']) + '.obj'


#  def normalise_vertex_references(data: [[str, [[str, list]]]]):
#  for _, etv, gtv, gd in data:
#  for t, d in gd:
#  if t == 'f':
#  for i in range(len(d)):
#  d[i] = list(map(lambda v: v - etv + gtv + 1, d[i]))

#  def make_abs_points(data: [[str, [[str, list]]]]):
#  for _, etv, gtv, gd in data:
#  for t, d in gd:
#  if t == 'f':
#  for i in range(len(d)):
#  d[i] = list(map(lambda v: v + gtv - 1, d[i]))

#  def make_rel_points(data:[[str, [[str, list]]]]):
#  for _,etv,gtv,gd in data:
#  for t,d in gd:
#  if t == 'f':
#  for i in range(len(d)):
#  d[i] = list(map(lambda v: v - gtv - 1, d[i]))


if __name__ == '__main__':
    try:
        exit(main(argv))
    except KeyboardInterrupt:
        exit(1)
