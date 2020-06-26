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
                      ox: float, oy: float) -> [dict]:
    return list(map(lambda d: resolve_position(d, ulen, dx, dy, ox, oy), data))


def resolve_position(data: dict, ulen: float, dx: float, dy: float, ox: float,
                     oy: float) -> dict:
    ret = dict(data)
    print(ret)
    ret['pos-x'] = ox + ulen * (ret['col'] + ret['off-x'] + ret['p-off-x'] - ret['glyph-width']/2) + dx * ret['num-dx']
    ret['pos-y'] = oy + ulen * (ret['row'] + ret['off-y'] + ret['p-off-y'] - ret['glyph-height']/2) + dy * ret['num-dy']
    return ret
