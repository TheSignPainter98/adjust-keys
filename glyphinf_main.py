#!/usr/bin/python3

from functools import reduce
from log import die, printe
from os.path import basename
from svgpathtools import svg2paths
from sys import argv, exit, stderr
from util import dict_union, list_diff
from xml.dom.minidom import Document, Element, parse
from yaml_io import write_yaml


def main(args: [str]) -> int:
    fargs:[str] = list(filter(lambda a: not a.startswith('-'), args[1:]))
    oargs:[str] = list(filter(lambda a: a.startswith('-'), args[1:]))

    if '-h' in oargs or '--help' in oargs:
        print('Usage: %s /path/to/glyphs/*.svg' % args[0])
        return 0
    if any(list(filter(lambda o: o not in ['-h', '--help'], oargs))):
        printe('Unrecognised arguments: %s' % ' '.join(list(filter(lambda o: o not in ['-h', '--help'], oargs))))
        return 1

    if len(fargs) == 0:
        die('Insufficient arguments, please pass at least one .svg file')
    elif any(list(filter(lambda a: not a.endswith('.svg'), fargs[1:]))):
        die('Only svg file-names are valid, the following have the wrong extension:', ' '.join(list(filter(lambda a: not a.endswith('.svg'), fargs[1:]))))

    glyphInf:dict = dict(reduce(lambda a,b: dict_union(a,b), map(lambda f: glyph_inf(basename(f)[:-4], f), fargs[1:]), {}))
    write_yaml('-', glyphInf)
    return 0


def glyph_inf(gname: str, gpath: str) -> dict:
    gfile: Document = parse(gpath).documentElement
    svg_width:float = float(gfile.attributes['width'].value)
    svg_height:float = float(gfile.attributes['height'].value)

    (paths,attrs) = svg2paths(gpath)
    if len(paths) > 0:
        (xmin,xmax,ymin,ymax) = paths[0].bbox()
        return {gname : { 'x': float(0.5 * (1 - (xmax + xmin)/svg_width)), 'y': float(0.5 * (1 - (ymax + ymin)/svg_height)), 'glyph-width': float((xmax - xmin)/svg_width), 'glyph-height': float((ymax - ymin)/svg_height), 'src': gpath }}
    else:
        die('No paths detected for glyph %s @ %s' %(gname, gpath))


def necessary_for_glyphs(gname:str, elem: Element) -> bool:
    return glyph_part(gname, elem) or has_glyph_child(gname, elem)


def glyph_part(gname:str, elem: Element) -> bool:
    return is_glyph(gname, elem) or (elem.parentNode and glyph_part(gname, elem.parentNode))


def has_glyph_child(gname:str, elem: Element) -> bool:
    # This line causes horrendous complexity and dynamic programming would have this sorted just fine, but I take no responsibility for my actions this day.
    return is_glyph(gname, elem) or (elem.childNodes and any(
        list(map(lambda c: has_glyph_child(gname, c), elem.childNodes))))


def is_glyph(gname:str, elem: Element) -> bool:
    return elem.attributes and 'id' in elem.attributes and elem.attributes['id'].value == gname


def node_list(elem: Element) -> [Element]:
    def append(l1: list, l2: list) -> list:
        return l1 + l2

    def fresh(e: list) -> list:
        return e if e else []

    return [elem] + list(
            reduce(append, list(map(node_list, fresh(elem.childNodes))), []))


if __name__ == '__main__':
    exit(main(argv))
