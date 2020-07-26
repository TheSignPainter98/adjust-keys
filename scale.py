# Copyright (C) Edward Jones

def get_scale(cap_unit_length: float, glyph_unit_length: float, dpi:float) -> float:
    return (cap_unit_length / glyph_unit_length) * (1000.0 * dpi)
