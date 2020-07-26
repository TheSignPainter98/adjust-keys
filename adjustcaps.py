#!/usr/bin/python3
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

from blender_available import blender_available

from args import parse_args
from argparse import Namespace
if blender_available():
    from bpy import context, data, ops
from concurrent.futures import ThreadPoolExecutor, wait
from copy import deepcopy
from functools import reduce
from layout import get_layout, parse_layout
from log import init_logging, printi, printw
from math import inf
from obj_io import read_obj, write_obj
from os import makedirs, remove, walk
from os.path import basename, exists, join
from positions import resolve_cap_position, translate_to_origin
from util import concat, dict_union, flatten_list, get_only, list_diff, inner_join, rem
from sys import argv, exit
from yaml_io import read_yaml


def main(*args: [[str]]) -> int:
    pargs: Namespace = parse_args(args)
    init_logging(pargs.verbosity)
    if not exists(pargs.output_dir):
        printi('Making non-existent directory "%s"' % pargs.output_dir)
        makedirs(pargs.output_dir, exist_ok=True)
    layout = get_layout(pargs.layout_file, pargs.layout_row_profile_file)
    adjust_caps(layout, pargs.cap_unit_length, pargs.cap_x_offset,
                pargs.cap_y_offset, pargs.cap_dir, pargs.output_dir,
                pargs.output_prefix, pargs.nprocs)

    return 0


def adjust_caps(layout: [dict], unit_length: float, x_offset: float,
                y_offset: float, cap_dir: str, output_dir: str,
                output_prefix: str, nprocs: int) -> str:
    # Resolve output unique output name
    caps: [dict] = get_data(layout, cap_dir)

    seen: dict = {}
    printi('Resolving cap output names')
    for cap in caps:
        if cap['cap-name'] not in seen:
            seen[cap['cap-name']] = 1
        else:
            seen[cap['cap-name']] += 1
        cap['oname'] = join(
            output_dir, output_prefix + '-' + cap['cap-name'] +
            ('-' +
             str(seen[cap['cap-name']]) if seen[cap['cap-name']] > 1 else '') +
            '.obj')

    printi('Adjusting and outputting caps on %d threads...' % nprocs)
    if nprocs == 1:
        # Run as usual, seems to help with the error reporting because reasons
        for cap in caps:
            handle_cap(cap, unit_length, x_offset, y_offset)
    else:
        with ThreadPoolExecutor(nprocs) as ex:
            cops: ['[dict,str]->()'] = [
                ex.submit(handle_cap, cap, unit_length, x_offset, y_offset)
                for cap in caps
            ]
            wait(cops)

    # Sequentially import the models (for thread-safety)
    if blender_available():
        objectsPreImport: [str] = data.objects.keys()
        for cap in caps:
            printi('Importing "%s" into blender...' % cap['oname'])
            ops.import_scene.obj(filepath=cap['oname'], axis_up='Z', axis_forward='Y')
            printi('Deleting file "%s"' % cap['oname'])
            remove(cap['oname'])
        objectsPostImport: [str] = data.objects.keys()
        importedCapObjectNames: [str] = list_diff(objectsPostImport,
                                                  objectsPreImport)
        importedCapObjects: [Object] = [
            o for o in data.objects if o.name in importedCapObjectNames
        ]
        printi('Successfully imported keycap objects')

        importedModelName: str = None
        if len(importedCapObjectNames) != 0:
            printi('Joining keycap models into a single object')
            ctx: dict = context.copy()

            ctx['object'] = ctx['active_object'] = importedCapObjects[0]
            ctx['selected_objects'] = ctx[
                'selected_editable_objects'] = importedCapObjects
            ops.object.join(ctx)

            printi('Renaming keycap model')
            objectsPreRename: [str] = data.objects.keys()
            importedCapObjects[0].name = importedCapObjects[
                0].data.name = 'capmodel'
            objectsPostRename: [str] = data.objects.keys()
            importedModelName = get_only(
                list_diff(objectsPostRename, objectsPreRename))
            printi('Keycap model renamed to "%s"' % importedModelName)
        return importedModelName
    else:
        return None


def get_data(layout: [dict], cap_dir: str) -> [dict]:
    printi('Finding and parsing cap models')
    caps: [dict] = get_caps(cap_dir)
    layout_with_caps: [dict] = inner_join(caps, 'cap-name', layout, 'cap-name')

    # Warn about missing models
    missing_models: [str] = list_diff(
        set(map(lambda cap: cap['cap-name'], layout)),
        set(map(lambda cap: cap['cap-name'], caps)))
    if missing_models != []:
        printw('Missing the following keycap models:\n\t' +
               '\n\t'.join(sorted(missing_models)))

    return layout_with_caps


def de_spookify(cap: dict) -> dict:
    return dict_union(rem(cap, 'cap-obj'),
                      {'cap-obj': deepcopy(cap['cap-obj'])})


def handle_cap(cap: dict, unit_length: float, x_offset: float,
               y_offset: float):
    printi('Adjusting cap %s' % cap['cap-name'])
    cap = de_spookify(cap)
    translate_to_origin(cap['cap-obj'])
    cap = resolve_cap_position(cap, unit_length, x_offset, y_offset)
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


def get_caps(cap_dir: str) -> [dict]:
    capFiles: [str] = []
    for (root, _, fnames) in walk(cap_dir):
        capFiles += list(
            map(lambda f: join(root, f),
                list(filter(lambda f: f.endswith('.obj'), fnames))))
    return list(
        map(lambda c: {
            'cap-name': basename(c)[:-4],
            'cap-source': c,
            'cap-obj': read_obj(c)
        }, capFiles))


def gen_cap_file_name(cap_loc: str, cap: dict) -> str:
    return (join(cap_loc, cap['profile-part'] + '_' + cap['width'])
            if 'key-type' not in cap else cap['key-type']) + '.obj'


if __name__ == '__main__':
    try:
        exit(main(argv))
    except KeyboardInterrupt:
        exit(1)
