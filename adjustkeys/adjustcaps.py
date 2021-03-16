#!/usr/bin/python3
# Copyright (C) Edward Jones


from .args import parse_args
from .blender_available import blender_available
from .layout import get_layout, parse_layout
from .lazy_import import LazyImport
from .log import die, init_logging, printe, printi, printw, print_warnings
from .obj_io import read_obj, write_obj
from .path import walk
from .positions import resolve_cap_position
from .util import concat, dict_union, flatten_list, get_dicts_with_duplicate_field_values, get_only, list_diff, inner_join, rem
from .uv_unwrap import uv_unwrap
from .yaml_io import read_yaml
from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor, wait
from copy import deepcopy
from math import inf, pi
from os import access, makedirs, remove, strerror, W_OK
from os.path import basename, exists, expanduser, join
from re import IGNORECASE, match
from statistics import mean
from sys import argv, exit

Collection:type = None
Euler:type = LazyImport('mathutils', 'Euler')
Matrix:type = LazyImport('mathutils', 'Matrix')
Vector:type = LazyImport('mathutils', 'Vector')
if blender_available():
    from bpy import ops
    from bpy.path import abspath
    from bpy.types import Collection
    data = LazyImport('bpy', 'data')
    context = LazyImport('bpy', 'context')


def adjust_caps(layout: [dict], colour_map:[dict], profile_data:dict, collection:Collection, layout_min_point:Vector, layout_max_point:Vector, pargs:Namespace) -> dict:
    # Resolve output unique output name
    printi('Getting required keycap data...')
    caps: [dict] = get_data(layout, pargs.cap_dir, colour_map, collection, profile_data)

    printi('Adjusting keycaps...')
    for cap in caps:
        handle_cap(cap, profile_data['unit-length'])

    capmodel_name:str = generate_capmodel_name('capmodel')
    uv_image_path:str = None
    uv_material_name:str = None
    colourMaterials:list = []
    importedModelName: str = None
    importedCapObjects:[Object] = list(map(lambda cap: cap['cap-obj'], caps))
    imgNode:ShaderNodeTexImage = None
    if len(importedCapObjects) != 0:
        # If shrink-wrapping, apply materials before the join
        if pargs.glyph_application_method == 'shrinkwrap':
            printi('Preparing individual materials')
            colourMaterials = generate_shrink_wrap_materials(pargs.use_existing_materials, colour_map, caps)
        else:
            uv_image_base:str = capmodel_name + '_uv_image.png'
            uv_image_path = abspath('//' + uv_image_base)
            if not check_permissions(uv_image_path, W_OK):
                uv_image_path = expanduser(join('~', 'Downloads', uv_image_base))

            printi('Handling material')
            (imgNode, colourMaterials) = generate_uv_map_materials(pargs.use_existing_materials, uv_image_path, capmodel_name, caps)
            if len(colourMaterials) != 0:
                uv_material_name = colourMaterials[0]

        printi('Joining keycap models into a single object')
        ctx: dict = {}
        joinTarget:Object = min(caps, key=lambda c: (c['cap-pos'].x, c['cap-pos'].y))['cap-obj']
        ctx['object'] = ctx['active_object'] = joinTarget
        ctx['selected_objects'] = ctx[
            'selected_editable_objects'] = importedCapObjects
        ops.object.join(ctx)

        printi('Renaming keycap model')
        objectsPreRename: [str] = data.objects.keys()
        joinTarget.name = joinTarget.data.name = capmodel_name
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

        if pargs.glyph_application_method == 'uv-map':
            printi('UV-unwrapping cap-model')
            layout_scale:float = profile_data['unit-length'] * profile_data['scale']
            uv_unwrap(obj, layout_scale * layout_min_point, layout_scale * layout_max_point, pargs.partition_uv_by_face_direction)

    return { 'keycap-model-name': importedModelName, 'material-names': colourMaterials, '~caps-with-margin-offsets': caps, '~texture-image-node': imgNode, 'uv-image-path': uv_image_path, 'uv-material-name': uv_material_name }

def check_permissions(fpath:str, perms:int) -> bool:
    try:
        return access(fpath, perms)
    except IOError as ioe:
        printe(strerror(ioe))
        return False

def generate_capmodel_name(intended_name:str) -> str:
    name:str = intended_name
    i:int = 1
    while name in data.objects:
        i += 1
        name = intended_name + '-' + str(i)
    return name

def generate_shrink_wrap_materials(use_existing_materials:bool, colour_map:[dict], caps:[dict]) -> [str]:
    colourMaterialsList:list = []
    colourMaterialsDict:dict = {}
    if colour_map is not None:
        colourMaterialsDict = { m['name'] : m for m in colour_map if 'cap-style' in m }
        for m in colourMaterialsDict.values():
            colourStr:str = str(m['cap-style'])
            colour:[float,float,float] = tuple([ float(int(colourStr[i:i+2], 16)) / 255.0 for i in range(0, len(colourStr), 2) ] + [1.0])
            if m['name'] not in data.materials.keys() or not use_existing_materials:
                m['material'] = data.materials.new(name=m['name'])
                m['material'].diffuse_color = colour
                colourMaterialsList.append(m['material'].name)
            else:
                m['material'] = data.materials[m['name']]
                colourMaterialsList.append(m['name'])

    # Apply materials
    printi('Applying material colourings...')
    for cap in caps:
        if cap['cap-style-rule'] is not None:
            colourRule:str = cap['cap-style-rule']
            colourStr:str = cap['cap-style']
            if colourRule not in colourMaterialsDict:
                colour:[float,float,float] = tuple([ float(int(colourStr[i:i+2], 16)) / 255.0 for i in range(0, len(colourStr), 2) ] + [1.0])
                colourMaterialsDict[colourRule]['material'] = data.materials.new(name=colourRule)
                colourMaterialsDict[colourRule]['material'].diffuse_color = colour
            cap['cap-obj'].data.materials.append(colourMaterialsDict[colourRule]['material'])
            cap['cap-obj'].active_material = colourMaterialsDict[colourRule]['material']

    return colourMaterialsList


def generate_uv_map_materials(use_existing_materials:str, uv_image_path:str, model_name:str, caps:[dict]) -> [str]:
    uv_material_name:str = model_name + '_material'
    if uv_material_name not in data.materials or not use_existing_materials:
        # Overwrite material if not using existing ones!
        if uv_material_name in data.materials:
            printw('Existing material named "%s" is overwritten, you may require the "use existing materials" option' % uv_material_name)
            data.materials.remove(data.materials[uv_material_name])
        mat = data.materials.new(name=uv_material_name)
        mat.use_nodes = True
        mat_nodes = mat.node_tree.nodes
        mat_edges = mat.node_tree.links

        # Get BSDF shader node
        bsdfNode:ShaderNodeBsdfPrincipled = mat_nodes['Principled BSDF']

        # Add coordinate and image nodes
        coordsNode:ShaderNodeTexCoord = mat_nodes.new('ShaderNodeTexCoord')
        imgNode:ShaderNodeTexImage = mat_nodes.new('ShaderNodeTexImage')

        # Position the new nodes relative to the old ones
        node_horizontal_margin_offset:Vector = Vector((300.0, 0.0))
        imgNode.location = bsdfNode.location - node_horizontal_margin_offset
        coordsNode.location = imgNode.location - node_horizontal_margin_offset

        # Add appropriate edges
        mat_edges.new(coordsNode.outputs['UV'], imgNode.inputs['Vector'])
        mat_edges.new(imgNode.outputs['Color'], bsdfNode.inputs['Base Color'])
    else:
        bpy_internal_uv_image_name:str = basename(uv_image_path)
        imgNode = get_only(
                [ n
                    for n in data.materials[uv_material_name].node_tree.nodes
                    if n.type == 'TEX_IMAGE'
                        and n.image is not None
                        and n.image.name is not None
                        and n.image.name.endswith(bpy_internal_uv_image_name)
                ],
                'No image node for "%s" found in material "%s" when trying to use existing materials for uv' % (bpy_internal_uv_image_name, uv_material_name),
                'Multiple image nodes for "%s" were found in material "%s" when trying to use existing materials for uv' % (bpy_internal_uv_image_name, uv_material_name)
            )

    for cap in caps:
        cap['cap-obj'].active_material = data.materials[uv_material_name]

    return (imgNode, [ uv_material_name ])


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
