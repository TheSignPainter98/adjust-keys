# Copyright (C) Edward Jones

from .lazy_import import LazyImport
from .log import printw
from math import cos, inf, sin

Matrix:type = LazyImport('mathutils', 'Matrix')
Vector:type = LazyImport('mathutils', 'Vector')


def resolve_glyph_position(data: dict, glyph_ulen: float, cap_ulen:float, scale:float) -> dict:
    ret: dict = dict(data)

    # Compute offset from top-left as if ret.rotation == 0
    offset:Vector = Matrix.Scale(glyph_ulen / cap_ulen, 2) @ Vector((ret['p-off-x'], ret['p-off-y'])) - ret['glyph-offset']

    # Apply offset with rotation
    ret['glyph-pos'] = glyph_ulen * ret['kle-pos'] + Matrix.Rotation(-ret['rotation'], 2) @ offset
    return ret


def resolve_cap_position(cap: dict, ulen: float) -> dict:
    # Compute cap position in R^2
    raw_cap_pos:Vector = ulen * cap['kle-pos'] + Matrix.Rotation(-cap['rotation'], 2) @ cap['margin-offset']

    # Convert to vector in R^3
    cap['cap-pos'] = Vector((raw_cap_pos.x, 0.0, raw_cap_pos.y))

    return cap
