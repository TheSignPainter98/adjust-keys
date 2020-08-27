#!/usr/bin/python3
# Copyright (C) Edward Jones


from .args import parse_args
from .blender_available import blender_available
from .layout import get_layout, parse_layout
from .log import die, init_logging, printi, printw
from .obj_io import read_obj, write_obj
from .path import walk
from .positions import resolve_cap_position, translate_to_origin
from .util import concat, dict_union, flatten_list, get_dicts_with_duplicate_field_values, get_only, list_diff, inner_join, rem
from .yaml_io import read_yaml
from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor, wait
from copy import deepcopy
from functools import reduce
from math import inf
from os import makedirs, remove
from os.path import basename, exists, join
from re import IGNORECASE, match
from sys import argv, exit
if blender_available():
    from bpy import context, data, ops


def main(*args: [[str]]) -> int:
    pargs: Namespace = parse_args(args)
    init_logging(pargs.verbosity)
    if not exists(pargs.output_dir):
        printi('Making non-existent directory "%s"' % pargs.output_dir)
        makedirs(pargs.output_dir, exist_ok=True)
    layout = get_layout(pargs.layout_file, pargs.layout_row_profile_file, pargs.homing_keys)
    if not blender_available():
        die('bpy is not available, please run adjustcaps from within Blender (instructions should be in the supplied README.md file)')

    adjust_caps(layout, pargs)

    return 0


def adjust_caps(layout: [dict], pargs:Namespace) -> dict:
    # Resolve output unique output name
    printi('Getting required keycap data...')
    caps: [dict] = get_data(layout, pargs.cap_dir, pargs.colour_map_file)

    colour_map:[dict] = read_yaml(pargs.colour_map_file)

    printi('Adjusting keycaps...')
    for cap in caps:
        handle_cap(cap, pargs.cap_unit_length, pargs.cap_x_offset, pargs.cap_y_offset, colour_map)

    # Sequentially import the models (for thread-safety)
    printi('Preparing material')
    colourMaterials:dict = { m['name'] : m for m in colour_map }
    for m in colourMaterials.values():
        colourStr:str = str(m['colour'])
        colour:[float,float,float] = tuple([ float(int(colourStr[i:i+2], 16)) / 255.0 for i in range(0, len(colourStr), 2) ] + [1.0])
        m['material'] = data.materials.new(name=m['name'])
        m['material'].diffuse_color = colour

    # Apply materials
    printi('Applying material colourings...')
    for cap in caps:
        if cap['cap-colour'] is not None:
            if cap['cap-colour'] not in colourMaterials:
                colourStr:str = cap['cap-colour']
                colour:[float,float,float] = tuple([ float(int(colourStr[i:i+2], 16)) / 255.0 for i in range(0, len(colourStr), 2) ] + [1.0])
                colourMaterials[colourStr] = { 'material': data.materials.new(name=cap['cap-colour']) }
                colourMaterials[colourStr]['material'].diffuse_color = colour
            cap['cap-obj'].data.materials.append(colourMaterials[cap['cap-colour']]['material'])
            cap['cap-obj'].active_material = colourMaterials[cap['cap-colour']]['material']

    importedModelName: str = None
    importedCapObjects:[Object] = list(map(lambda cap: cap['cap-obj'], caps))
    if len(importedCapObjects) != 0:
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


def get_data(layout: [dict], cap_dir: str, colour_map_file:str) -> [dict]:
    printi('Finding and parsing cap models')
    # Get caps, check for duplicates
    caps: [dict] = get_caps(cap_dir)
    duplicate_cap_names:[str] = list(map(lambda c: c[1][0]['cap-name'] + ' @ ' + ', '.join(list(map(lambda c2: c2['cap-source'], c[1]))), get_dicts_with_duplicate_field_values(caps, 'cap-name').items()))
    if duplicate_cap_names != []:
        printw('Duplicate keycap names detected:\n\t' + '\n\t'.join(duplicate_cap_names))
    layout_with_caps: [dict] = inner_join(caps, 'cap-name', layout, 'cap-name')

    # Import necessary cap models
    firsts:dict = {}
    for cap_data in layout_with_caps:
        if cap_data['cap-source'] not in firsts:
            # Import new object
            printi('Importing "%s" into blender...' % cap_data['cap-source'])
            objectsPreSingleImport:[str] = data.objects.keys()
            ops.import_scene.obj(filepath=cap_data['cap-source'], axis_up='Z', axis_forward='Y')
            objectsPostSingleImport:[str] = data.objects.keys()
            cap_data['cap-obj-name'] = get_only(list_diff(objectsPostSingleImport, objectsPreSingleImport), 'No new id was added when importing from %s' % cap_data['cap-source'], 'Multiple ids changed when importing %s, got %%d new: %%s' % cap_data['cap-source'])
            cap_data['cap-obj'] = context.scene.objects[cap_data['cap-obj-name']]
            firsts[cap_data['cap-source']] = cap_data['cap-obj']
        else:
            # Duplicate existing object
            printi('Duplicating existing "%s"...' % cap_data['cap-source'])
            objectsPreCopy:[str] = data.objects.keys()
            original_obj = firsts[cap_data['cap-source']].copy()
            objectsPostCopy:[str] = data.objects.keys()
            cap_data['cap-obj-name'] = get_only(list_diff(objectsPostCopy, objectsPreCopy), 'No new id was added when copying from %s' % cap_data['cap-source'], 'Multiple ids changed when copying %s, got %%d new: %%s' % cap_data['cap-source'])
            new_obj = original_obj.copy()
            new_obj.data = original_obj.data.copy()
            cap_data['cap-obj'] = new_obj
            context.scene.collection.objects.link(new_obj)

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


def handle_cap(cap: dict, unit_length: float, cap_x_offset: float,
        cap_y_offset: float, colour_map:[dict]):
    printi('Adjusting cap %s' % cap['cap-name'])
    translate_to_origin(cap['cap-obj'])
    cap = resolve_cap_position(cap, unit_length, cap_x_offset, cap_y_offset)
    cap = apply_cap_position(cap)
    printi('Resolving colour of cap %s' % cap['cap-name'])
    cap = apply_colour(cap, colour_map)


def apply_colour(cap:dict, colour_map:[dict]) -> dict:
    cap_name:str = cap['key']
    if 'cap-colour-raw' in cap:
        cap['cap-colour'] = cap['cap-colour-raw']
        return cap
    for mapping in colour_map:
        if any(list(map(lambda r: match('^' + r + '$', cap_name, IGNORECASE) is not None, mapping['keys']))):
            cap['cap-colour'] = mapping['name']
            return cap
    cap['cap-colour'] = None
    return cap


def apply_cap_position(cap: dict) -> dict:
    cap['cap-obj'].location = (cap['pos-x'], cap['pos-y'], cap['pos-z'])
    return cap


def get_caps(cap_dir: str) -> [dict]:
    capFiles: [str] = list(filter(lambda f: f.endswith('.obj'), walk(cap_dir)))
    return list(
        map(lambda c: {
            'cap-name': basename(c)[:-4],
            'cap-source': c,
        }, capFiles))


if __name__ == '__main__':
    try:
        exit(main(argv))
    except KeyboardInterrupt:
        exit(1)
