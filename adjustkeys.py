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

from functools import reduce
from layout import parse_layout
from log import die, init_logging
from glyphinf import glyph_inf
from os import walk
from os.path import exists, join
from positions import resolve_positions
from util import concat, dict_union, inner_join, list_diff, rob_rem
from xml.dom.minidom import Element, parseString
from yaml_io import read_yaml


def adjust_keys(verbosity: int, profile_file: str,
                layout_row_profile_file: str, glyph_dir: str, layout_file: str,
                glyph_map_file: str, unit_length: int, global_x_offset: int,
                global_y_offset: int) -> [dict]:
    init_logging(verbosity)
    data: [dict] = collect_data(profile_file, layout_row_profile_file,
                                glyph_dir, layout_file, glyph_map_file)

    placed_glyphs: [dict] = resolve_positions(data, unit_length,
                                              global_x_offset, global_y_offset)

    for i in range(len(placed_glyphs)):
        with open(placed_glyphs[i]['src'], 'r', encoding='utf-8') as f:
            placed_glyphs[i] = dict_union(
                placed_glyphs[i],
                {'svg': parseString(f.read()).documentElement})
        remove_guide_from_cap(placed_glyphs[i]['svg'])
        placed_glyphs[i]['vector'] = ['<g transform="translate(%f %f)">' %(placed_glyphs[i]['pos-x'], placed_glyphs[i]['pos-y'])] + list(map(lambda c: c.toxml(), (filter(lambda c: type(c) == Element, placed_glyphs[i]['svg'].childNodes)))) + ['</g>']

    svgWidth: int = max(list(map(lambda p: p['pos-x'], placed_glyphs)),
                        default=0) + unit_length
    svgHeight: int = max(list(map(lambda p: p['pos-y'], placed_glyphs)),
                         default=0) + unit_length
    svg: str = '\n'.join([
        '<svg width="%d" height="%d" viewbox="0 0 %d %d" fill="none" xmlns="http://www.w3.org/2000/svg">'
        % (svgWidth, svgHeight, svgWidth, svgHeight)
    ] + list(map(lambda p: '\n'.join(p['vector']) if 'vector' in p else '', placed_glyphs)) + ['</svg>'])

    return svg


def remove_guide_from_cap(cap:Element) -> Element:
    def _remove_guide_from_cap(cap:Element) -> None:
        badKids:[Element] = list(filter(lambda k: k.attributes and 'id' in k.attributes and k.attributes['id'].value == 'cap-guide', cap.childNodes))
        goodKids:[Element] = list_diff(list(cap.childNodes), badKids)
        for badKid in badKids:
            cap.removeChild(badKid)
        for goodKid in goodKids:
            _remove_guide_from_cap(goodKid)
    _remove_guide_from_cap(cap)
    return cap


def collect_data(profile_file: str, layout_row_profile_file: str,
                 glyph_dir: str, layout_file: str,
                 glyph_map_file: str) -> [dict]:
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
    profile_special_offsets_rel: [dict] = list(
        map(
            lambda m: {
                'key-type': m[0],
                'p-off-x': m[1]['x'] if 'x' in m[1] else 0.0,
                'p-off-y': m[1]['y'] if 'y' in m[1] else 0.0
            }, profile['special-offsets'].items()))
    layout_row_profiles: [str] = read_yaml(layout_row_profile_file)
    glyph_offsets = list(map(glyph_inf, glyph_files(glyph_dir)))
    layout: [dict] = parse_layout(layout_row_profiles, read_yaml(layout_file))
    glyph_map = read_yaml(glyph_map_file)
    glyph_map_rel = list(
        map(lambda m: {
            'key': m[0],
            'glyph': m[1]
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


def glyph_files(dname: str) -> [str]:
    if not exists(dname):
        die('Directory "%s" doesn\'t exist' % dname)
    svgs: [str] = []
    for (root, _, fnames) in walk(dname):
        svgs += list(
            map(lambda f: join(root, f),
                list(filter(lambda f: f.endswith('.svg'), fnames))))
    if svgs == []:
        die('Couldn\'t find any svgs in directory "%s"' % dname)
    return svgs
