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
from .util import concat, dict_union, frange, get_dicts_with_duplicate_field_values, get_only, inner_join, list_diff, rob_rem, safe_get
from .yaml_io import read_yaml, write_yaml
from functools import reduce
from os import remove
from os.path import exists, join
from math import degrees
from mathutils import Matrix, Vector
from re import IGNORECASE, match
from sys import argv, exit
from types import LambdaType
from xml.dom.minidom import Element, parseString
Collection:type = None
if blender_available():
    from bpy import ops
    from bpy.types import Collection
    data = LazyImport('bpy', 'data')

adjusted_svg_file_name:str = get_temp_file_name()

##
# @brief Entry point function, should be treated as the first thing called
#
# @param args:[str] Command line arguments
#
# @return Zero if and only if the program is to exit successfully
def adjust_glyphs(layout:[dict], profile_data:dict, margin_offset:float, collection:Collection, glyph_map:dict, pargs:Namespace) -> [str]:
    glyph_data: [dict] = collect_data(layout, profile_data, margin_offset, pargs.glyph_dir, glyph_map, pargs.iso_enter_glyph_pos, pargs.alignment)
    scale:float = get_scale(profile_data['unit-length'], pargs.glyph_unit_length, pargs.svg_units_per_mm)

    placed_glyphs: [dict] = list(map(lambda glyph: resolve_glyph_position(glyph, pargs.glyph_unit_length, profile_data['unit-length'], profile_data['scale']), glyph_data))

    for i in range(len(placed_glyphs)):
        with open(placed_glyphs[i]['src'], 'r', encoding='utf-8') as f:
            placed_glyphs[i] = dict_union(
                placed_glyphs[i],
                {'svg': parseString(f.read()).documentElement})
        remove_guide_from_cap(placed_glyphs[i]['svg'], pargs.glyph_part_ignore_regex)
        style:str = get_style(placed_glyphs[i])
        if style:
            remove_fill_from_svg(placed_glyphs[i]['svg'])
        placed_glyphs[i]['vector'] = get_glyph_vector_data(placed_glyphs[i], style)

    svgWidth: int = max(map(lambda p: p['glyph-pos'].x, placed_glyphs),
                        default=0) + 10.0 * pargs.glyph_unit_length
    svgHeight: int = max(map(lambda p: p['glyph-pos'].y, placed_glyphs),
                         default=0) + 10.0 * pargs.glyph_unit_length
    svg: str = '\n'.join([
        '<svg width="%d" height="%d" viewbox="0 0 %d %d" fill="none" xmlns="http://www.w3.org/2000/svg">'
        % (svgWidth, svgHeight, svgWidth, svgHeight)
    ] + list(
        map(lambda p: '\n'.join(p['vector'])
            if 'vector' in p else '', placed_glyphs)) + ['</svg>'])

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

    printi('Adding svg into the right collection')
    glyph_collection = make_collection('glyphs', parent_collection=collection)
    #  collection.children.link(glyph_collection)
    for svgObjectName in svgObjectNames:
        glyph_collection.objects.link(data.objects[svgObjectName])
    data.collections.remove(data.collections[collectionName])

    # Apprpriately scale the objects
    printi('Scaling glyphs and moving origins')
    for svgObjectName in svgObjectNames:
        svgObject = data.objects[svgObjectName]
        svgObject.data.transform(Matrix.Scale(scale * profile_data['scale'], 4))

    # Clean away temporary files.
    if exists(adjusted_svg_file_name):
        printi('Cleaning away the placed-glyph svg file')
        remove(adjusted_svg_file_name)

    printi('Successfully imported svg objects')

    return { 'glyph-names': svgObjectNames } if svgObjectNames is not None else {}


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

def resolve_special_profile_y_offsets_with_alignment(alignment:str, iso_enter_glyph_pos:str, unit_length:float, margin_offset:float, x_offsets:dict, y_offsets:dict, special_y_offsets:dict) -> dict:
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

    resolved_offsets['iso-enter'] = { 'x': iso_enter_x, 'y': iso_enter_y + margin_offset }

    # Resolve num-plus and num-enter
    unit_offgen:LambdaType = lambda yo: { 'x': x_offsets[1], 'y': yo + margin_offset }
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

def collect_data(layout: [dict], profile: dict, margin_offset:float, glyph_dir: str,
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
            'p-off-y': m[1] + margin_offset
        }, profile['y-offsets'].items()))
    profile_special_offsets:dict = resolve_special_profile_y_offsets_with_alignment(alignment, iso_enter_glyph_pos, profile['unit-length'], margin_offset, profile_x_offsets, profile['y-offsets'], profile['special-offsets'])
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

    key_offsets = inner_join(glyph_map_rel, 'glyph', glyph_offsets, 'glyph')
    glyph_offset_layout = inner_join(key_offsets, 'key', layout, 'key')
    profile_x_offset_keys = inner_join(glyph_offset_layout, 'width',
                                       profile_x_offsets_rel, 'width')
    profile_x_y_offset_keys = inner_join(profile_x_offset_keys, 'profile-part',
                                         profile_y_offsets_rel, 'profile-part')
    data = list(
        map(
            lambda k: k if 'key-type' not in k else dict_union(
                k,
                list(
                    filter(lambda s: s['key-type'] == k['key-type'],
                           profile_special_offsets_rel))[0]),
            profile_x_y_offset_keys))

    glyphs_lost_due_to_profile_data:{str} = set(list_diff(list_diff(map(lambda g: g['glyph'], profile_x_y_offset_keys), glyph_names), missing_glyphs))
    if len(glyphs_lost_due_to_profile_data) != 0:
        printw('The following glyphs were lost when inner-joining with the offset information\n\t' + '\n\t'.join(list(sorted(glyphs_lost_due_to_profile_data))))

    return data

def get_style(key:dict) -> str:
    if safe_get(key, 'glyph-style') is not None:
        raw_style:str = key['glyph-style']
        if match('^[0-9a-f]{6}$', key['glyph-style'], IGNORECASE) is not None:
            # Apply RGB colour
            style = 'style="fill:#%s;"' % raw_style
        else:
            # Otherwise assume CSS has been written
            if not raw_style.endswith(';'):
                raw_style += ';'
            style = 'style="%s"' % raw_style.replace('\\', '\\\\').replace('"', '\\"')
        return style
    else:
        return None

def get_glyph_vector_data(glyph:dict, style:str) -> [str]:
    # Prepare header content
    transformations:[str] = [
            'translate(%f %f)' % (glyph['glyph-pos'].x, glyph['glyph-pos'].y)
        ]
    if 'rotation' in glyph:
        transformations.append('rotate(%f)' % -degrees(glyph['rotation']))
    header_content:[str] = [ 'transform="%s"' % ' '.join(transformations), style ]

    # Prepare svg content
    svg_content:[str] = list(map(lambda c: c.toxml(), map(sanitise_ids, filter(lambda c: type(c) == Element, glyph['svg'].childNodes))))

    # Combine and return
    return [ '<g %s>' % ' '.join(header_content) ] + svg_content + [ '</g>' ]

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

def glyph_files(dname: str) -> [str]:
    if not exists(dname):
        die('Directory "%s" doesn\'t exist' % dname)
    svgs: [str] = list(filter(lambda f: f.endswith('.svg'), walk(dname)))
    if svgs == []:
        die('Couldn\'t find any svgs in directory "%s"' % dname)
    return svgs
