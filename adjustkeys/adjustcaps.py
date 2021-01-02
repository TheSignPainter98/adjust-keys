#!/usr/bin/python3
# Copyright (C) Edward Jones


from .args import parse_args
from .blender_available import blender_available
from .layout import get_layout, parse_layout
from .lazy_import import LazyImport
from .log import die, init_logging, printi, printw, print_warnings
from .obj_io import read_obj, write_obj
from .path import walk
from .positions import resolve_cap_position
from .util import concat, dict_union, flatten_list, get_dicts_with_duplicate_field_values, get_only, list_diff, inner_join, rem
from .yaml_io import read_yaml
from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor, wait
from copy import deepcopy
from math import inf, pi
from mathutils import Euler, Matrix, Vector
from os import makedirs, remove
from os.path import basename, exists, join
from re import IGNORECASE, match
from statistics import mean
from sys import argv, exit
Collection:type = None
if blender_available():
    from bpy import ops
    from bpy.types import Collection
    data = LazyImport('bpy', 'data')
    context = LazyImport('bpy', 'context')


def adjust_caps(layout: [dict], colour_map:[dict], profile_data:dict, collection:Collection, pargs:Namespace) -> dict:
    # Resolve output unique output name
    printi('Getting required keycap data...')
    caps: [dict] = get_data(layout, pargs.cap_dir, colour_map, collection, profile_data)

    printi('Adjusting keycaps...')
    for cap in caps:
        handle_cap(cap, profile_data['unit-length'])

    # Sequentially import the models
    printi('Preparing materials')
    colourMaterials:dict = {}
    if colour_map is not None:
        colourMaterials = { m['name'] : m for m in colour_map if 'cap-colour' in m }
        for m in colourMaterials.values():
            colourStr:str = str(m['cap-colour'])
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
        ctx: dict = {}
        joinTarget:Object = min(caps, key=lambda c: (c['cap-pos'].x, c['cap-pos'].y))['cap-obj']
        ctx['object'] = ctx['active_object'] = joinTarget
        ctx['selected_objects'] = ctx[
            'selected_editable_objects'] = importedCapObjects
        ops.object.join(ctx)

        printi('Renaming keycap model')
        objectsPreRename: [str] = data.objects.keys()
        intended_name:str = 'capmodel'
        i:int = 1
        while intended_name in data.objects:
            i += 1
            intended_name = 'capmodel' + '-' + str(i)
        joinTarget.name = joinTarget.data.name = intended_name
        objectsPostRename: [str] = data.objects.keys()
        importedModelName = get_only(
                list_diff(objectsPostRename, objectsPreRename), 'No new id was created by blender when renaming the keycap model', 'Multiple new ids were created when renaming the keycap model (%d new): %s')
        printi('Keycap model renamed to "%s"' % importedModelName)

        printi('Ensuring imported cap model object only linked in the new collection')
        imp_obj:object = data.objects[importedModelName]
        for coll in imp_obj.users_collection:
            coll.objects.unlink(imp_obj)
        collection.objects.link(imp_obj)

        printi('Updating cap-model scaling')
        obj:Object = data.objects[importedModelName]
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Scale(profile_data['scale'], 4)

        printi('Applying outstanding cap-model transforms')
        obj.data.transform(obj.matrix_world)
        obj.matrix_world = Matrix.Identity(4)

    # Compute average margin offset. Arrumes the input data isn't too horrible.
    average_margin_offset:float = mean(list(map(lambda c: c['margin-offset'][1], caps)))

    return { 'keycap-model-name': importedModelName, 'material-names': list(colourMaterials.keys()), 'margin-offset': average_margin_offset }


def get_data(layout: [dict], cap_dir: str, colour_map:[dict], collection:Collection, profile_data:dict) -> [dict]:
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
            ops.import_scene.obj(filepath=cap_data['cap-source'])
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
            collection.objects.link(new_obj)

    # Warn about missing models
    missing_models: [str] = list_diff(
        set(map(lambda cap: cap['cap-name'], layout)),
        set(map(lambda cap: cap['cap-name'], caps)))
    if missing_models != []:
        printw('Missing the following keycap models:\n\t' +
               '\n\t'.join(sorted(missing_models)))

    layout_with_caps_with_margins = list(map(lambda c: get_margin_offset(c, profile_data['unit-length']), layout_with_caps))

    return layout_with_caps_with_margins


def handle_cap(cap: dict, unit_length: float):
    printi('Adjusting cap %s' % cap['cap-name'])
    cap = resolve_cap_position(cap, unit_length)
    cap = apply_cap_pose(cap)


def apply_cap_pose(cap: dict) -> dict:
    obj:object = cap['cap-obj']

    # Original offset
    original_off:Vector = Vector(obj.bound_box[0])

    # Reset pose
    obj.matrix_world = Matrix.Identity(4)

    # Set rotation
    obj.matrix_world @= Matrix.Rotation(pi/2.0, 4, 'X')
    obj.matrix_world @= Matrix.Rotation(cap['rotation'], 4, 'Y')

    # Move to correct position from origin
    obj.matrix_world @= Matrix.Translation(-original_off)
    obj.matrix_world @= Matrix.Translation(Matrix.Rotation(-cap['rotation'], 4, 'Y') @ cap['cap-pos'])

    return cap


def get_caps(cap_dir: str) -> [dict]:
    capFiles: [str] = list(filter(lambda f: f.endswith('.obj'), walk(cap_dir)))
    return list(
        map(lambda c: {
            'cap-name': basename(c)[:-4],
            'cap-source': c,
        }, capFiles))

def get_margin_offset(cap:dict, unit_length:float) -> dict:
    printi('Computing cap margin offset of keycap "%s"' % cap['key'])

    cap_dims:Vector = Vector((cap['cap-obj'].dimensions.x, cap['cap-obj'].dimensions.z))
    unit_dims:Vector = Vector((max(cap['width'], cap['secondary-width'] if 'secondary-width' in cap else -1.0), max(cap['height'], cap['secondary-height'] if 'secondary-height' in cap else -1.0)))

    cap['margin-offset'] = (unit_length * unit_dims - cap_dims) / 2.0
    return cap
