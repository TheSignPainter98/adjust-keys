#!/usr/bin/python3
# Copyright (C) Edward Jones

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
from path import init_path, fwalk
from positions import resolve_cap_position, translate_to_origin
from re import IGNORECASE, match
from sys import argv, exit
from util import concat, dict_union, flatten_list, get_dicts_with_duplicate_field_values, get_only, list_diff, inner_join, rem
from yaml_io import read_yaml


def main(*args: [[str]]) -> int:
    pargs: Namespace = parse_args(args)
    init_logging(pargs.verbosity)
    init_path(pargs.path)
    if not exists(pargs.output_dir):
        printi('Making non-existent directory "%s"' % pargs.output_dir)
        makedirs(pargs.output_dir, exist_ok=True)
    layout = get_layout(pargs.layout_file, pargs.layout_row_profile_file, pargs.homing_keys)
    adjust_caps(layout, pargs)

    return 0


def adjust_caps(layout: [dict], pargs:Namespace) -> dict:
    # Resolve output unique output name
    caps: [dict] = get_data(layout, pargs.cap_dir, pargs.colour_map_file)

    seen: dict = {}
    printi('Resolving cap output names')
    for cap in caps:
        if cap['cap-name'] not in seen:
            seen[cap['cap-name']] = 1
        else:
            seen[cap['cap-name']] += 1
        cap['oname'] = join(
            pargs.output_dir, pargs.output_prefix + '-' + cap['cap-name'] +
            ('-' +
             str(seen[cap['cap-name']]) if seen[cap['cap-name']] > 1 else '') +
            '.obj')

    colour_map:[dict] = read_yaml(pargs.colour_map_file)

    printi('Adjusting and outputting caps on %d thread%s...' %(pargs.nprocs, 's' if pargs.nprocs != 1 else ''))
    if pargs.nprocs == 1:
        # Run as usual, seems to help with the error reporting because reasons
        for cap in caps:
            handle_cap(cap, pargs.cap_unit_length, pargs.cap_x_offset, pargs.cap_y_offset)
    else:
        with ThreadPoolExecutor(pargs.nprocs) as ex:
            cops: ['[dict,str]->()'] = [
                ex.submit(handle_cap, cap, pargs.cap_unit_length, pargs.cap_x_offset, pargs.cap_y_offset)
                for cap in caps
            ]
            wait(cops)

    # Sequentially import the models (for thread-safety)
    if blender_available():
        printi('Preparing material')
        colourMaterials:dict = { m['name'] : m for m in colour_map }
        for m in colourMaterials.values():
            colourStr:str = str(m['colour'])
            colour:[float,float,float] = tuple([ float(int(colourStr[i:i+2], 16)) / 255.0 for i in range(0, len(colourStr), 2) ] + [1.0])
            m['material'] = data.materials.new(name=m['name'])
            m['material'].diffuse_color = colour

        objectsPreImport: [str] = data.objects.keys()
        for cap in caps:
            printi('Importing "%s" into blender...' % cap['oname'])
            objectsPreSingleImport:[str] = data.objects.keys()
            ops.import_scene.obj(filepath=cap['oname'], axis_up='Z', axis_forward='Y')
            objectsPostSingleImport:[str] = data.objects.keys()
            cap['imported-name'] = get_only(list_diff(objectsPostSingleImport, objectsPreSingleImport), 'No new id was added when importing from %s' % cap['oname'], 'Multiple ids changed when importing %s, got %%d new: %%s' % cap['oname'])
            cap['imported-object'] = context.scene.objects[cap['imported-name']]
            printi(cap['imported-name'])
            printi('Applying material to %s' % cap['oname'])
            if cap['cap-colour'] is not None:
                cap['imported-object'].data.materials.append(colourMaterials[cap['cap-colour']]['material'])
                cap['imported-object'].active_material = colourMaterials[cap['cap-colour']]['material']
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
                    list_diff(objectsPostRename, objectsPreRename), 'No new id was created by blender when renaming the keycap model', 'Multiple new ids were created when renaming the keycap model (%d new): %s')
            printi('Keycap model renamed to "%s"' % importedModelName)
        return { 'keycap-model-name': importedModelName, 'material-names': list(colourMaterials.keys()) }
    else:
        return {}


def get_data(layout: [dict], cap_dir: str, colour_map_file:str) -> [dict]:
    printi('Finding and parsing cap models')
    # Get caps, check for duplicates
    caps: [dict] = get_caps(cap_dir)
    duplicate_cap_names:[str] = list(map(lambda c: c[1][0]['cap-name'] + ' @ ' + ', '.join(list(map(lambda c2: c2['cap-source'], c[1]))), get_dicts_with_duplicate_field_values(caps, 'cap-name').items()))
    if duplicate_cap_names != []:
        printw('Duplicate keycap names detected:\n\t' + '\n\t'.join(duplicate_cap_names))
    layout_with_caps: [dict] = inner_join(caps, 'cap-name', layout, 'cap-name')

    colour_map:[dict] = read_yaml(colour_map_file)
    layout_with_caps:[dict] = list(map(lambda cap: apply_colour(cap, colour_map), layout_with_caps))

    # Warn about missing models
    missing_models: [str] = list_diff(
        set(map(lambda cap: cap['cap-name'], layout)),
        set(map(lambda cap: cap['cap-name'], caps)))
    if missing_models != []:
        printw('Missing the following keycap models:\n\t' +
               '\n\t'.join(sorted(missing_models)))

    return layout_with_caps


def apply_colour(cap:dict, colour_map:[dict]) -> dict:
    cap_name:str = cap['key']
    for mapping in colour_map:
        if any(list(map(lambda r: match('^' + r + '$', cap_name, IGNORECASE) is not None, mapping['keys']))):
            cap['cap-colour'] = mapping['name']
            return cap
    cap['cap-colour'] = None
    return cap


def de_spookify(cap: dict) -> dict:
    return dict_union(rem(cap, 'cap-obj'),
                      {'cap-obj': deepcopy(cap['cap-obj'])})


def handle_cap(cap: dict, unit_length: float, cap_x_offset: float,
        cap_y_offset: float):
    printi('Adjusting cap %s' % cap['cap-name'])
    cap = de_spookify(cap)
    translate_to_origin(cap['cap-obj'])
    cap = resolve_cap_position(cap, unit_length, cap_x_offset, cap_y_offset)
    cap = apply_cap_position(cap)
    printi('Resolving colour of cap %s' % cap['oname'])
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
    capFiles: [str] = list(filter(lambda f: f.endswith('.obj'), fwalk(cap_dir)))
    return list(
        map(lambda c: {
            'cap-name': basename(c)[:-4],
            'cap-source': c,
            'cap-obj': read_obj(c)
        }, capFiles))


if __name__ == '__main__':
    try:
        exit(main(argv))
    except KeyboardInterrupt:
        exit(1)
