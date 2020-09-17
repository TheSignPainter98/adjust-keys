#!/usr/bin/python3
# Copyright (C) Edward Jones

from .args import parse_args, Namespace
from .blender_available import blender_available
from .glyphinf import glyph_inf
from .layout import get_layout, parse_layout
from .lazy_import import LazyImport
from .log import die, init_logging, printi, printw, print_warnings
from .path import walk
from .positions import resolve_glyph_positions
from .scale import get_scale
from .util import concat, dict_union, get_dicts_with_duplicate_field_values, inner_join, list_diff, rob_rem
from .yaml_io import read_yaml, write_yaml
from functools import reduce
from os import remove
from os.path import exists, join
from re import match
from sys import argv, exit
from xml.dom.minidom import Element, parseString
if blender_available():
    from bpy import ops
    data = LazyImport('bpy', 'data')


##
# @brief Entry point function, should be treated as the first thing called
#
# @param args:[str] Command line arguments
#
# @return Zero if and only if the program is to exit successfully
def adjust_glyphs(layout:[dict], pargs:Namespace) -> [str]:
    glyph_data: [dict] = collect_data(layout, pargs.profile_file, pargs.glyph_dir, pargs.glyph_map_file, pargs.iso_enter_glyph_pos)
    scale:float = get_scale(pargs.cap_unit_length, pargs.glyph_unit_length, pargs.svg_units_per_mm)

    placed_glyphs: [dict] = resolve_glyph_positions(glyph_data, pargs.glyph_unit_length,
                                                    pargs.global_x_offset,
                                                    pargs.global_y_offset)

    for i in range(len(placed_glyphs)):
        with open(placed_glyphs[i]['src'], 'r', encoding='utf-8') as f:
            placed_glyphs[i] = dict_union(
                placed_glyphs[i],
                {'svg': parseString(f.read()).documentElement})
        remove_guide_from_cap(placed_glyphs[i]['svg'], pargs.glyph_part_ignore_regex)
        placed_glyphs[i]['vector'] = [
            '<g transform="translate(%f %f)">' %
            (placed_glyphs[i]['pos-x'], placed_glyphs[i]['pos-y'])
        ] + list(
            map(lambda c: c.toxml(),
                (filter(lambda c: type(c) == Element,
                        placed_glyphs[i]['svg'].childNodes)))) + ['</g>']

    svgWidth: int = max(list(map(lambda p: p['pos-x'], placed_glyphs)),
                        default=0) + pargs.glyph_unit_length
    svgHeight: int = max(list(map(lambda p: p['pos-y'], placed_glyphs)),
                         default=0) + pargs.glyph_unit_length
    svg: str = '\n'.join([
        '<svg width="%d" height="%d" viewbox="0 0 %d %d" fill="none" xmlns="http://www.w3.org/2000/svg">'
        % (svgWidth, svgHeight, svgWidth, svgHeight)
    ] + list(
        map(lambda p: '\n'.join(p['vector'])
            if 'vector' in p else '', placed_glyphs)) + ['</svg>'])

    output_location: str = pargs.output_prefix + '.svg'
    printi('Writing to file "%s"' % output_location)
    svgObjectNames: str = None
    with open(output_location, 'w+') as f:
        print(svg, file=f)

    printi('Importing svg into blender')
    objectsPreImport: [str] = data.objects.keys()
    ops.import_curve.svg(filepath=output_location)
    objectsPostImport: [str] = data.objects.keys()

    # Rename the svg
    svgObjectNames = list_diff(objectsPostImport, objectsPreImport)

    # Apprpriately scale the objects
    printi('Scaling glyphs')
    for svgObjectName in svgObjectNames:
        data.objects[svgObjectName].scale *= scale

    # Clean output
    if exists(output_location):
        printi('Deleting file "%s"' % output_location)
        remove(output_location)
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


def collect_data(layout: [dict], profile_file: str, glyph_dir: str,
        glyph_map_file: str, iso_enter_glyph_pos:str) -> [dict]:
    profile: dict = read_yaml(profile_file)
    profile_x_offsets_rel: [dict] = list(
        map(lambda m: {
            'width': m[0],
            'p-off-x': m[1]
        }, profile['x-offsets'].items()))
    profile_y_offsets_rel: [dict] = list(
        map(lambda m: {
            'profile-part': m[0],
            'p-off-y': m[1]
        }, profile['y-offsets'].items()))
    profile_special_offsets_rel: [dict] = list(map(lambda so: parse_special_pos(so, iso_enter_glyph_pos), profile['special-offsets'].items()))
    glyph_offsets = list(map(glyph_inf, glyph_files(glyph_dir)))
    duplicate_glyphs:[str] = list(map(lambda c: c[1][0]['glyph'] + ' @ ' + ', '.join(list(map(lambda c2: c2['src'], c[1]))), get_dicts_with_duplicate_field_values(glyph_offsets, 'glyph').items()))
    if duplicate_glyphs != []:
        printw('Duplicate glyphs detected:\n\t' + '\n\t'.join(duplicate_glyphs))
    glyph_map = read_yaml(glyph_map_file)
    glyph_map_rel = list(
        map(lambda m: {
            'key': str(m[0]),
            'glyph': str(m[1])
        }, glyph_map.items()))

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

    return data

def parse_special_pos(special_offset:[str, dict], iso_enter_glyph_pos:str) -> dict:
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
                'p-off-x': special_offset[1]['x'] if 'x' in special_offset[1] else 0.5,
                'p-off-y': special_offset[1]['y'] if 'y' in special_offset[1] else 0.5
            }

def glyph_files(dname: str) -> [str]:
    if not exists(dname):
        die('Directory "%s" doesn\'t exist' % dname)
    svgs: [str] = list(filter(lambda f: f.endswith('.svg'), walk(dname)))
    if svgs == []:
        die('Couldn\'t find any svgs in directory "%s"' % dname)
    return svgs
