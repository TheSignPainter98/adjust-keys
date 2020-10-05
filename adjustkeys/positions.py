# Copyright (C) Edward Jones

from .log import printw
from math import cos, inf, sin
from mathutils import Matrix, Vector


def resolve_glyph_position(data: dict, glyph_ulen: float, cap_ulen:float, margin:float) -> dict:
    ret: dict = dict(data)
    # Compute offset from top-left if ret.rotation = 0
    col_off: float = glyph_ulen * ret['p-off-x'] / cap_ulen - 0.5 * ret['glyph-src-width']
    row_off: float = glyph_ulen * ret['p-off-y'] / cap_ulen - 0.5 * ret['glyph-src-height']
    # Apply offset with the right rotation
    ret['pos-x'] = glyph_ulen * ret['col'] + col_off * cos(ret['rotation']) + row_off * sin(ret['rotation'])
    ret['pos-y'] = glyph_ulen * ret['row'] - col_off * sin(ret['rotation']) + row_off * cos(ret['rotation'])
    return ret


def resolve_cap_position(cap: dict, ulen: float) -> dict:
    cap['pos-x'] = ulen * cap['col']
    cap['pos-y'] = ulen * cap['row'] * -1
    cap['pos-z'] = 0.0
    return cap


def move_object_origin_to_global_origin_with_offset(obj:object, cap_x_offset:float, cap_y_offset:float):
    vec_from_origin:Vector = Vector([cap_x_offset, -cap_y_offset, 0.0]) - Vector(obj.bound_box[3])
    obj.data.transform(Matrix.Translation(vec_from_origin))
    obj.matrix_world.translation -= vec_from_origin
