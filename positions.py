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

from log import printw
from math import inf


def resolve_glyph_positions(data: [dict], ulen: float, gx: float,
                            gy: float) -> [dict]:
    return list(map(lambda d: resolve_glyph_position(d, ulen, gx, gy), data))


def resolve_glyph_position(data: dict, ulen: float, gx: float,
                           gy: float) -> dict:
    ret: dict = dict(data)
    # Compute the centre of the keycap
    kx: float = gx + ulen * (ret['p-off-x'] + ret['col'])
    ky: float = gy + ulen * (ret['p-off-y'] + ret['row'])
    # Compute the location of the top left corner of the glyph svg from the centre of a keycap
    cx: float = -0.5 * ret['glyph-src-width']
    cy: float = -0.5 * ret['glyph-src-height']
    # Compute compute where to place the svg
    ret['pos-x'] = kx + cx
    ret['pos-y'] = ky + cy
    return ret


def resolve_cap_position(cap: dict, ulen: float, mx: float, my: float,
                         plane: str) -> dict:
    plane_x_dir: str
    plane_y_dir: str
    plane_z_dir: str

    if plane.lower() == 'z':
        plane_x_dir = 'pos-x'
        plane_y_dir = 'pos-y'
        plane_z_dir = 'pos-z'
    elif plane.lower() == 'y':
        printw(
            'Arranging along the plane whose normal is the positive y-axis is not yet supported, using the default'
        )
        plane_x_dir = 'pos-x'
        plane_y_dir = 'pos-y'
        plane_z_dir = 'pos-z'
    elif plane.lower() == 'z':
        printw(
            'Arranging along the plane whose normal is the positive y-axis is not yet supported, using the default'
        )
        plane_x_dir = 'pos-x'
        plane_y_dir = 'pos-y'
        plane_z_dir = 'pos-z'

    cap[plane_x_dir] = ulen * cap['col'] + mx
    cap[plane_y_dir] = -1 * (ulen * cap['row'] + my)
    cap[plane_z_dir] = 0.0

    return cap


def translate_to_origin(data: [[str, [[str, list]]]], plane: str):
    # Translate each group to the origin
    for _, _, _, gd in data:
        # Obtain minimum points in x, y and z
        exts: [float] = [
                inf * (1 if plane != 'x' else -1),
                inf * (1 if plane != 'y' else -1),
                inf * (1 if plane != 'z' else -1),
            ]
        funcs:['[float,float] -> float'] = [
                min if plane != 'x' else max,
                min if plane != 'y' else max,
                min if plane != 'z' else max
            ]
        for t, d in gd:
            if t == 'v':
                for i in range(len(d)):
                    exts[i] = funcs[i](exts[i], d[i])
        # Translate by offset to origin
        for t, d in gd:
            if t == 'v':
                for i in range(len(d)):
                    d[i] -= exts[i]
