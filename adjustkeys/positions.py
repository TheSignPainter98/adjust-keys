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


def resolve_cap_position(cap: dict, ulen: float) -> dict:
    cap['pos-x'] = ulen * cap['col']
    cap['pos-y'] = ulen * cap['row'] * -1
    cap['pos-z'] = 0.0
    return cap


def move_object_origin_to_global_origin_with_offset(obj:object, cap_x_offset:float, cap_y_offset:float):
    vec_from_origin:Vector = Vector([cap_x_offset, -cap_y_offset, 0.0]) - Vector(obj.bound_box[3])
    obj.data.transform(Matrix.Translation(vec_from_origin))
    obj.matrix_world.translation += -vec_from_origin
