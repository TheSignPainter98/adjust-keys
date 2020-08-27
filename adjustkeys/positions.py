# Copyright (C) Edward Jones

from .log import printw
from math import inf
from mathutils import Matrix, Vector


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


def resolve_cap_position(cap: dict, ulen: float, ox: float, oy: float) -> dict:
    cap['pos-x'] = ulen * cap['col'] + ox
    cap['pos-y'] = -1 * (ulen * cap['row'] + oy)
    cap['pos-z'] = 0.0

    return cap


def translate_to_origin(cap_obj:object):
    cap_obj.data.transform(Matrix.Translation(-Vector(cap_obj.bound_box[3])))
    cap_obj.matrix_world.translation += Vector(cap_obj.bound_box[3])
