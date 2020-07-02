#!/usr/bin/python3

from functools import reduce
from log import die, printe
from os.path import basename
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
    elif any(list(filter(lambda a: not a.endswith('.svg'), fargs))):
        die('Only svg file-names are valid, the following have the wrong extension:', ' '.join(list(filter(lambda a: not a.endswith('.svg'), fargs))))

    glyphInf:dict = dict(reduce(lambda a,b: dict_union(a,b), map(lambda f: glyph_inf(f), fargs), {}))
    write_yaml('-', glyphInf)
    return 0


def glyph_inf(gpath: str) -> dict:
    gname:str = basename(gpath)[:-4]
    gfile: Document = parse(gpath).documentElement
    svg_width:float = float(gfile.attributes['width'].value)
    svg_height:float = float(gfile.attributes['height'].value)
    return { 'glyph': gname, 'glyph-src-width': float(svg_width), 'glyph-src-height': float(svg_height), 'src': gpath }


if __name__ == '__main__':
    exit(main(argv))
