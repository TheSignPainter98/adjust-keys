#!/usr/bin/python3
# Copyright (C) Edward Jones

from mathutils import Vector
from os.path import basename
from re import search
from xml.dom.minidom import Document, parse

numRegex:str = r'([0-9]*\.[0-9]+|[0-9]+)'

def glyph_inf(gpath: str) -> dict:
    gname: str = glyph_name(gpath)
    gfile: Document = parse(gpath).documentElement
    rawWidth:str = search(numRegex, gfile.attributes['width'].value).group(0)
    rawHeight:str = search(numRegex, gfile.attributes['height'].value).group(0)
    svg_width: float = float(rawWidth)
    svg_height: float = float(rawHeight)
    return {
        'glyph': gname,
        'glyph-dim': Vector((float(svg_width), float(svg_height))),
        'src': gpath
    }

def glyph_name(gpath:str) -> str:
    return basename(gpath)[:-4]
