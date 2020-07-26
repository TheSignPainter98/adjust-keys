#!/usr/bin/python3
# Copyright (C) Edward Jones

from os.path import basename
from xml.dom.minidom import Document, parse


def glyph_inf(gpath: str) -> dict:
    gname: str = glyph_name(gpath)
    gfile: Document = parse(gpath).documentElement
    svg_width: float = float(gfile.attributes['width'].value)
    svg_height: float = float(gfile.attributes['height'].value)
    return {
        'glyph': gname,
        'glyph-src-width': float(svg_width),
        'glyph-src-height': float(svg_height),
        'src': gpath
    }

def glyph_name(gpath:str) -> str:
    return basename(gpath)[:-4]
