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


def resolve_positions(data: [dict], ulen: float, dx: float, dy: float,
        gx: float, gy: float) -> [dict]:
    return list(map(lambda d: resolve_position(d, ulen, dx, dy, gx, gy), data))


def resolve_position(data: dict, ulen: float, dx: float, dy: float, gx: float,
        gy: float) -> dict:
    ret:dict = dict(data)
    # Compute the centre of the keycap
    kx:float = gx + ulen * (ret['p-off-x'] + ret['col']) + dx * ret['num-dx']
    ky:float = gy + ulen * (ret['p-off-y'] + ret['row']) + dy * ret['num-dy']
    # Compute the location of the top left corner of the glyph svg from the centre of a keycap
    cx:float = - 0.5 * ret['glyph-src-width']
    cy:float = - 0.5 * ret['glyph-src-height']
    # Compute compute where to place the svg
    ret['pos-x'] = kx + cx
    ret['pos-y'] = ky + cy
    return ret
