#!/usr/bin/python3
# Copyright (C) Edward Jones

from .args import parse_args, Namespace
from .blender_available import blender_available
from .collections import make_collection
from .glyphinf import glyph_inf
from .input_types import type_check_glyph_map
from .layout import get_layout, parse_layout
from .lazy_import import LazyImport
from .log import die, init_logging, printi, printw, print_warnings
from .path import get_temp_file_name, walk
from .positions import resolve_glyph_position
from .scale import get_scale
from .shrink_wrap import shrink_wrap_glyphs_to_keys
from .util import concat, dict_union, frange, get_dicts_with_duplicate_field_values, get_only, inner_join, right_outer_join, list_diff, rob_rem, safe_get
from .yaml_io import read_yaml, write_yaml
from functools import reduce
from os import remove
from os.path import basename, exists, join
from math import degrees
from mathutils import Matrix, Vector
from re import IGNORECASE, match
from sys import argv, exit
from types import LambdaType
from wand.color import Color as Colour
from wand.image import Image
from xml.dom.minidom import Element, parseString
Collection:type = None
if blender_available():
    from bpy import ops
    from bpy.types import Collection, ShaderNodeTexImage
    data = LazyImport('bpy', 'data')

##
# @brief Entry point function, should be treated as the first thing called
#
# @param args:[str] Command line arguments
#
# @return Zero if and only if the program is to exit successfully
def adjust_glyphs(layout:[dict], profile_data:dict, model_name:str, layout_dims:Vector, collection:Collection, glyph_map:dict, imgNode:ShaderNodeTexImage, uv_image_path:str, uv_material_name:str, pargs:Namespace) -> [str]:
    glyph_data: [dict] = collect_data(layout, profile_data, pargs.glyph_dir, glyph_map, pargs.iso_enter_glyph_pos, pargs.alignment)
    scale:float = get_scale(safe_get(profile_data, 'unit-length', default=1.0), pargs.glyph_unit_length, pargs.svg_units_per_mm)

    offset_resolved_glyphs: [dict] = map(lambda glyph: resolve_glyph_offset(glyph, pargs.alignment if glyph['key'] != 'iso-enter' else pargs.iso_enter_glyph_pos, pargs.glyph_unit_length), glyph_data)
    placed_glyphs: [dict] = list(map(lambda glyph: resolve_glyph_position(glyph, pargs.glyph_unit_length, profile_data['unit-length'], profile_data['scale']), offset_resolved_glyphs))

    for i in range(len(placed_glyphs)):
        glyph_style:str = get_style(placed_glyphs[i], 'glyph-style')
        if 'src' in placed_glyphs[i]:
            with open(placed_glyphs[i]['src'], 'r', encoding='utf-8') as f:
                placed_glyphs[i] = dict_union(
                    placed_glyphs[i],
                    {'svg': parseString(f.read()).documentElement})
            remove_guide_from_cap(placed_glyphs[i]['svg'], pargs.glyph_part_ignore_regex)
            if glyph_style:
                remove_fill_from_svg(placed_glyphs[i]['svg'])
        placed_glyphs[i]['vector'] = get_glyph_vector_data(placed_glyphs[i], glyph_style, pargs.glyph_unit_length, pargs.glyph_application_method, pargs.partition_uv_by_face_direction, layout_dims)

    svg_dims:Vector
    if pargs.partition_uv_by_face_direction:
        svg_dims = pargs.glyph_unit_length * Matrix.Diagonal((1, 2)) @ layout_dims
    else:
        svg_dims = pargs.glyph_unit_length * layout_dims

    svg: str = '\n'.join([
        '<svg width="%d" height="%d" viewbox="0 0 %d %d" fill="none" xmlns="http://www.w3.org/2000/svg">'
        % (svg_dims.x, svg_dims.y, svg_dims.x, svg_dims.y)
    ] + list(
        map(lambda p: '\n'.join(p['vector'])
            if 'vector' in p else '', placed_glyphs)) + ['</svg>'])

    svgObjectNames:[str] = None
    if pargs.glyph_application_method == 'shrinkwrap':
        svgObjectNames = import_and_align_glyphs_as_curves(scale, profile_data, model_name, collection, svg, pargs)
    else:
        import_and_align_glyphs_as_raster(svg, imgNode, uv_image_path, uv_material_name, layout_dims, pargs.uv_res, pargs.partition_uv_by_face_direction)

    printi('Successfully imported glyphs')

    return { 'glyph-names': svgObjectNames } if svgObjectNames is not None else {}

def import_and_align_glyphs_as_curves(scale:float, profile_data:dict, keycapModelName:str, collection:Collection, svg:str, pargs:Namespace):
    adjusted_svg_file_name:str = get_temp_file_name()

    printi('Writing svg to file "%s"' % adjusted_svg_file_name)
    with open(adjusted_svg_file_name, 'w+') as f:
        f.write(svg)

    printi('Importing svg into blender')
    collectionsPreImport:[str] = data.collections.keys()
    objectsPreImport: [str] = data.objects.keys()
    ops.import_curve.svg(filepath=adjusted_svg_file_name)
    objectsPostImport: [str] = data.objects.keys()
    collectionsPostImport:[str] = data.collections.keys()
    svgObjectNames:[str] = list_diff(objectsPostImport, objectsPreImport)
    collectionName:str = get_only(list_diff(collectionsPostImport, collectionsPreImport), 'No collections added when importing glyphs', 'Multiple collections added whilst importing glyphs, got %d: %s')

    printi("Adding svg into the correct collection")
    for svgObjectName in svgObjectNames:
        collection.objects.link(data.objects[svgObjectName])
    data.collections.remove(data.collections[collectionName])

    # Apprpriately scale the objects
    printi('Scaling glyphs')
    for svgObjectName in svgObjectNames:
        svgObject = data.objects[svgObjectName]
        svgObject.data.transform(Matrix.Scale(scale * profile_data['scale'], 4))

    # Clean away temporary files.
    if exists(adjusted_svg_file_name):
        printi('Cleaning away the placed-glyph svg file')
        remove(adjusted_svg_file_name)

    # Shrink-wrap if models were imported
    if pargs.adjust_caps:
        subsurf_params:dict = {
                'viewport-levels': pargs.subsurf_viewport_levels,
                'render-levels': pargs.subsurf_render_levels,
                'quality': pargs.subsurf_quality,
                'adaptive-subsurf': pargs.adaptive_subsurf
            }
        shrink_wrap_glyphs_to_keys(svgObjectNames, keycapModelName, profile_data['unit-length'], pargs.shrink_wrap_offset, subsurf_params, profile_data['scale'])

    return svgObjectNames

def import_and_align_glyphs_as_raster(svg:str, imgNode:ShaderNodeTexImage, uv_image_path:str, uv_material_name:str, layout_dims:Vector, uv_res:float, partition_uv_by_face_direction:bool):
    # Convert to png
    #  from cairosvg import svg2png
    #  m:float = min((Matrix.Diagonal((1, 2)) @ layout_dims) if partition_uv_by_face_direction else layout_dims)
    #  uv_dims:Vector = (uv_res / m) * layout_dims
    #  svg2png_params:dict = {
        #  'parent_width': int(uv_dims.x),
        #  'parent_height': int(uv_dims.y),
        #  'scale': m,
        #  #  'unsafe': True,
        #  'output_width': int(uv_dims.x),
        #  'output_height': int(uv_dims.y) * (2 if partition_uv_by_face_direction else 1), # Who knows why this is required for the cairo method, but it seems to do the job
        #  'write_to': uv_image_path,
    #  }
    #  svg2png(svg, **svg2png_params)

    png:bytes
    m:float = min((Matrix.Diagonal((1, 2)) @ layout_dims) if partition_uv_by_face_direction else layout_dims)
    uv_dims:Vector = (uv_res / m) * layout_dims
    with Colour('transparent') as transparent:
        image_params:dict = {
            'blob': svg.encode('utf-8'),
            'format': 'svg',
            'background': transparent,
            'width': int(uv_dims.x),
            'height': int(uv_dims.y),
        }
        with Image(**image_params) as image:
            png = image.make_blob(format='png')
    with open(uv_image_path, 'wb+') as ofile:
        ofile.write(png)

    # Add image to Blender's database if absent otherwise update
    bpy_internal_uv_image_name:str = basename(uv_image_path)
    if bpy_internal_uv_image_name not in data.images:
        imgNode.image = data.images.load(uv_image_path, check_existing=False) # TODO: delay this
    else:
        imgNode.image = data.images[bpy_internal_uv_image_name]
        imgNode.image.reload()


def resolve_glyph_offset(cap:dict, alignment:str, glyph_ulen:float) -> dict:
    if 'glyph-dim' not in cap:
        cap['glyph-offset'] = Vector((0.0, 0.0))
        return cap

    # Functions and mapping for placement
    alignment_xy_map:dict = {
        'top': 'left',
        'middle': 'centre',
        'bottom': 'right'
    }
    offset_funcs:dict = {
        'left': lambda _: 0.5 * glyph_ulen,
        'centre': lambda w: w / 2.0,
        'right': lambda w: w - 0.5 * glyph_ulen
    }

    # Appropriately apply mapping funcs
    alignment_parts:[str] = alignment.split('-')
    cap['glyph-offset'] = Vector((offset_funcs[alignment_parts[1]](cap['glyph-dim'].x), offset_funcs[alignment_xy_map[alignment_parts[0]]](cap['glyph-dim'].y)))
    return cap


def remove_guide_from_cap(cap: Element, glyph_part_ignore_regex) -> Element:
    def _remove_guide_from_cap(cap: Element, glyph_part_ignore_regex) -> None:
        badKids: [Element] = list(
            filter(
                lambda k: k.attributes and 'id' in k.attributes and match(
                    glyph_part_ignore_regex, k.attributes['id'].value),
                cap.childNodes))
        goodKids: [Element] = list_diff(list(cap.childNodes), badKids)
        for badKid in badKids:
            cap.removeChild(badKid)
        for goodKid in goodKids:
            _remove_guide_from_cap(goodKid, glyph_part_ignore_regex)

    _remove_guide_from_cap(cap, glyph_part_ignore_regex)
    return cap

def resolve_profile_x_offsets_with_alignment(alignment:str, unit_length:float, smallest:float=0.5, largest:float=14.0, step:float=0.25) -> dict:
    alignment_funcs:dict = {
            'left': lambda _: 0.5,
            'centre': lambda w: w / 2.0,
            'right': lambda w: w - 0.5
        }
    alignment_func:LambdaType = alignment_funcs[alignment.split('-')[1]]
    return { w: unit_length * alignment_func(w) for w in frange(smallest, largest, step) }

def resolve_special_profile_y_offsets_with_alignment(alignment:str, iso_enter_glyph_pos:str, unit_length:float, x_offsets:dict, y_offsets:dict, special_y_offsets:dict) -> dict:
    resolved_offsets:dict = {}

    # Resolve aligned iso-enter glyph x-offsets
    iso_enter_x_offsets:dict = resolve_profile_x_offsets_with_alignment(iso_enter_glyph_pos, unit_length, smallest=1.25, largest=1.5)
    iso_enter_x:float
    iso_enter_glyph_pos_parts:[str] = iso_enter_glyph_pos.split('-')
    if iso_enter_glyph_pos_parts[0] == 'top':
        iso_enter_x = iso_enter_x_offsets[1.5]
    else:
        iso_enter_x = 0.25 * unit_length + iso_enter_x_offsets[1.25]

    # Resolve aligned iso-enter glyph y-offsets
    iso_enter_y:float
    if iso_enter_glyph_pos_parts[0] == 'top':
        iso_enter_y = y_offsets['R3']
    elif iso_enter_glyph_pos_parts[0] == 'middle':
        iso_enter_y = special_y_offsets['iso-enter']
    else:
        iso_enter_y = unit_length + y_offsets['R2']

    resolved_offsets['iso-enter'] = { 'x': iso_enter_x, 'y': iso_enter_y }

    # Resolve num-plus and num-enter
    unit_offgen:LambdaType = lambda yo: { 'x': x_offsets[1], 'y': yo }
    alignment_direction:str = alignment.split('-')[0]
    if alignment_direction == 'top':
        resolved_offsets['num-plus'] = unit_offgen(y_offsets['R3'])
        resolved_offsets['num-enter'] = unit_offgen(y_offsets['R1'])
    elif alignment_direction == 'middle':
        resolved_offsets['num-plus'] = unit_offgen(special_y_offsets['num-plus'])
        resolved_offsets['num-enter'] = unit_offgen(special_y_offsets['num-enter'])
    elif alignment_direction == 'bottom':
        resolved_offsets['num-plus'] = unit_offgen(unit_length + y_offsets['R2'])
        resolved_offsets['num-enter'] = unit_offgen(unit_length + y_offsets['R1'])

    return resolved_offsets

def collect_data(layout: [dict], profile: dict, glyph_dir: str,
        glyph_map: dict, iso_enter_glyph_pos:str, alignment:str) -> [dict]:
    profile_x_offsets:dict = resolve_profile_x_offsets_with_alignment(alignment, profile['unit-length'])
    profile_x_offsets_rel: [dict] = list(
        map(lambda m: {
            'width': m[0],
            'p-off-x': m[1]
        }, profile_x_offsets.items()))
    profile_y_offsets_rel: [dict] = list(
        map(lambda m: {
            'profile-part': m[0],
            'p-off-y': m[1]
        }, profile['y-offsets'].items()))
    profile_special_offsets:dict = resolve_special_profile_y_offsets_with_alignment(alignment, iso_enter_glyph_pos, profile['unit-length'], profile_x_offsets, profile['y-offsets'], profile['special-offsets'])
    profile_special_offsets_rel: [dict] = list(map(lambda so: { 'key-type': so[0], 'p-off-x': so[1]['x'], 'p-off-y': so[1]['y'] }, profile_special_offsets.items()))

    glyph_offsets = list(map(glyph_inf, glyph_files(glyph_dir)))
    glyph_names:{str} = set(map(lambda g: g['glyph'], glyph_offsets))
    duplicate_glyphs:[str] = list(map(lambda c: c[1][0]['glyph'] + ' @ ' + ', '.join(list(map(lambda c2: c2['src'], c[1]))), get_dicts_with_duplicate_field_values(glyph_offsets, 'glyph').items()))
    if duplicate_glyphs != []:
        printw('Duplicate glyphs detected:\n\t' + '\n\t'.join(duplicate_glyphs))
    glyph_map_rel = list(
        map(lambda m: {
            'key': str(m[0]),
            'glyph': str(m[1])
        }, glyph_map.items()))

    missing_glyphs:{str} = set(list_diff(map(str, glyph_map.values()), glyph_names))
    if len(missing_glyphs) != 0:
        printw('The following glyphs could not be found:\n\t' + '\n\t'.join(list(sorted(missing_glyphs))))

    key_offsets:[dict] = inner_join(glyph_map_rel, 'glyph', glyph_offsets, 'glyph')
    glyph_offset_layout:[dict] = right_outer_join(key_offsets, 'key', layout, 'key')
    profile_x_offset_keys:[dict] = inner_join(glyph_offset_layout, 'width',
                                       profile_x_offsets_rel, 'width')
    profile_x_y_offset_keys:[dict] = inner_join(profile_x_offset_keys, 'profile-part',
                                         profile_y_offsets_rel, 'profile-part')
    all_keys_offset:[dict] = list(
        map(
            lambda k: k if 'key-type' not in k else dict_union(
                k,
                list(
                    filter(lambda s: s['key-type'] == k['key-type'],
                           profile_special_offsets_rel))[0]),
            profile_x_y_offset_keys))

    glyphs_lost_due_to_profile_data:{str} = set(list_diff(list_diff(map(lambda g: g['glyph'], filter(lambda g: 'glyph' in g, profile_x_y_offset_keys)), glyph_names), missing_glyphs))
    if len(glyphs_lost_due_to_profile_data) != 0:
        printw('The following glyphs were lost when inner-joining with the offset information\n\t' + '\n\t'.join(list(sorted(glyphs_lost_due_to_profile_data))))

    # Apply cap-specific vertical marign offsets (as the profile data y-offset value does not include margins)
    all_keys_with_vertical_margin_offsets_applied:[dict] = list(map(apply_vertical_margin_offset, all_keys_offset))

    return all_keys_with_vertical_margin_offsets_applied

def get_style(key:dict, style_key:str) -> str:
    raw_style:str = safe_get(key, style_key)
    if raw_style is not None:
        if match('^[0-9a-f]{6}$', raw_style, IGNORECASE) is not None:
            # Apply RGB colour
            style = 'style="fill:#%s;"' % raw_style
        else:
            # Otherwise assume CSS has been written
            if not raw_style.endswith(';'):
                raw_style += ';'
            style = 'style="%s"' % raw_style.replace('\\', '\\\\').replace('"', '\\"')
        return style
    else:
        printw('Style key "%s" not present in whichever rule was intended for key "%s"' % (style_key, key['key']))
        return ''

def get_glyph_vector_data(glyph:dict, style:str, ulen:float, glyph_application_method:float, partition_uv_by_face_direction:bool, layout_dims:Vector) -> [str]:
    # Prepare glyph header contnet
    glyph_transformations:[str] = [
            'translate(%f %f)' % (glyph['glyph-pos'].x, glyph['glyph-pos'].y),
            'rotate(%f)' % -degrees(glyph['rotation']),
        ]
    glyph_svg_header_content:[str] = [ 'transform="%s"' % ' '.join(glyph_transformations) ]
    if style:
        glyph_svg_header_content.append(style)

    #  # Prepare svg content
    glyph_svg_content:[str] = []
    glyph_svg_data:[str] = []
    if 'svg' in glyph:
        glyph_svg_content = list(map(lambda c: c.toxml(), map(sanitise_ids, filter(lambda c: type(c) == Element, glyph['svg'].childNodes))))
        glyph_svg_data = [ '<g %s>' % ' '.join(glyph_svg_header_content) ] + glyph_svg_content + [ '</g>' ]

    cap_svg_data:[str] = []
    if glyph_application_method == 'uv-map':
        cap_svg_content:[str] = generate_cap_svg_content(glyph, ulen)

        # Compute colouring for the top
        cap_top_pos:Vector = ulen * glyph['kle-pos']
        cap_top_transformations:[str] = [
            'translate(%f %f)' % (cap_top_pos.x, cap_top_pos.y),
            'rotate(%f)' % -degrees(glyph['rotation'])
        ]
        cap_top_svg_header:[str] = [ 'transform="%s"' % ' '.join(cap_top_transformations) ]

        # Compute colouring for the bottom if separate
        if partition_uv_by_face_direction:
            cap_bottom_pos:Vector = ulen * (glyph['kle-pos'] + Matrix.Diagonal((0, 1)) @ layout_dims)
            cap_bottom_transformations:[str] = [
                'translate(%f %f)' % (cap_bottom_pos.x, cap_bottom_pos.y),
                'rotate(%f)' % -degrees(glyph['rotation'])
            ]
            cap_bottom_svg_header:[str] = [ 'transform="%s"' % ' '.join(cap_bottom_transformations) ]

        cap_svg_data:[str] = [ '<g %s>' % ' '.join(cap_top_svg_header) ] + cap_svg_content + [ '</g>' ]
        if partition_uv_by_face_direction:
            cap_svg_data += [ '<g %s>' % ' '.join(cap_bottom_svg_header) ] + cap_svg_content + [ '</g>' ]

    # Combine and return
    return ['<g>'] + cap_svg_data + glyph_svg_data + ['</g>']

def generate_cap_svg_content(glyph:dict, ulen:float) -> [str]:
    svg_content:[str]
    cap_style:str = get_style(glyph, 'cap-style')
    if 'key-type' in glyph and glyph['key-type'] == 'iso-enter':
        svg_content = [
                '<rect width="%f" height="%f" %s />' % (1.5 * ulen, ulen, cap_style),
                '<rect width="%f" height="%f" transform="translate(%f %f)" %s />' % (1.25 * ulen, ulen, 0.25 * ulen, ulen, cap_style)
            ]
    else:
        svg_content = [ '<rect width="%f" height="%f" %s />' % (ulen * glyph['secondary-width'], ulen * glyph['secondary-height'], cap_style) ]
    return svg_content

def sanitise_ids(node:Element) -> Element:
    if node.attributes and 'id' in node.attributes.keys():
        original_name:str = node.getAttribute('id')
        sanitised_id:str = original_name
        i:int = 1
        while sanitised_id in data.objects:
            i += 1
            sanitised_id = original_name + '-' + str(i)
        node.setAttribute('id', sanitised_id)
    for child in node.childNodes:
        sanitise_ids(child)
    return node

def remove_fill_from_svg(node:Element):
    if node.attributes and 'fill' in node.attributes.keys():
        node.removeAttribute('fill')
    for child in node.childNodes:
        remove_fill_from_svg(child)

def parse_special_pos(special_offset:[str, dict], iso_enter_glyph_pos:str, default_x_offset:float) -> dict:
    if special_offset[0] == 'iso-enter':
        if iso_enter_glyph_pos not in special_offset[1].keys():
            die('Could not find key %s in iso-enter offset spec' % iso_enter_glyph_pos)
        return {
                'key-type': special_offset[0],
                'p-off-x': special_offset[1][iso_enter_glyph_pos]['x'],
                'p-off-y': special_offset[1][iso_enter_glyph_pos]['y'],
            }
    else:
        return {
                'key-type': special_offset[0],
                'p-off-x': special_offset[1]['x'] if 'x' in special_offset[1] else default_x_offset,
                'p-off-y': special_offset[1]['y']
            }

def apply_vertical_margin_offset(cap:dict) -> dict:
    if 'margin-offset' in cap:
        cap['p-off-y'] += cap['margin-offset'][1]
    return cap

def glyph_files(dname: str) -> [str]:
    if not exists(dname):
        die('Directory "%s" doesn\'t exist' % dname)
    svgs: [str] = list(filter(lambda f: f.endswith('.svg'), walk(dname)))
    if svgs == []:
        die('Couldn\'t find any svgs in directory "%s"' % dname)
    return svgs
