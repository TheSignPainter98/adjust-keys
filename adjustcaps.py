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

from concurrent.futures import ThreadPoolExecutor, wait
from copy import deepcopy
from layout import parse_layout
from log import init_logging, printi
from math import inf
from multiprocessing import cpu_count
from obj_io import read_obj, write_obj
from os import walk
from os.path import basename, exists, join
from positions import resolve_cap_position, translate_to_origin
from util import dict_union, inner_join, rem
from yaml_io import read_yaml


def adjust_caps(verbosity: int, unit_length: float, x_offset: float,
        y_offset: float, plane: str, profile_file: str, cap_dir: str, output_dir:str,
        layout_file: str, layout_row_profile_file: str):
    init_logging(verbosity)
    printi('Reading layout information')
    layout_row_profiles: [str] = read_yaml(layout_row_profile_file)
    layout: [dict] = list(
            map(add_cap_name,
                parse_layout(layout_row_profiles, read_yaml(layout_file))))

    printi('Finding and parsing cap models')
    caps: [dict] = get_caps(cap_dir)
    layout_with_caps:[dict] = inner_join(caps, 'cap-name', layout, 'cap-name')

    # Resolve output unique output name
    seen:dict = {}
    printi('Resolving cap output names')
    for cap in layout_with_caps:
        if cap['cap-name'] not in seen:
            seen[cap['cap-name']] = 1
        else:
            seen[cap['cap-name']] += 1
        cap['oname'] = join(output_dir, 'capmodel-' + cap['cap-name'] + ('-' + str(seen[cap['cap-name']]) if seen[cap['cap-name']] > 1 else '') + '.obj')

    nprocs:int = 2 * cpu_count()
    printi('Adjusting and outputting caps on %d threads...' % nprocs)
    with ThreadPoolExecutor(nprocs) as ex:
        ops:['[dict,str]->()'] = [ ex.submit(handle_cap, cap, unit_length, x_offset, y_offset, plane) for cap in layout_with_caps ]
        wait(ops)

    return list(map(lambda c: c['oname'], layout_with_caps))

def de_spookify(cap:dict) -> dict:
    return dict_union(rem(cap, 'cap-obj'), {'cap-obj': deepcopy(cap['cap-obj'])})

def handle_cap(cap:dict, unit_length:float, x_offset:float, y_offset:float, plane:str):
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


