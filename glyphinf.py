#!/usr/bin/python3

from os.path import basename
from xml.dom.minidom import Document, parse


def glyph_inf(gpath: str) -> dict:
    gname: str = basename(gpath)[:-4]
    gfile: Document = parse(gpath).documentElement
    svg_width: float = float(gfile.attributes['width'].value)
    svg_height: float = float(gfile.attributes['height'].value)
    return {
        'glyph': gname,
        'glyph-src-width': float(svg_width),
        'glyph-src-height': float(svg_height),
        'src': gpath
    }
