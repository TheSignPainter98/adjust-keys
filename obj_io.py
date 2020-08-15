# Copyright (C) Edward Jones

from functools import reduce
from log import die, printi
from os.path import exists
from path import fopen
from util import concat
from sys import stdout

# Keeps the python parser happy when looking at type annotations. It doesn't even use them so it doesn't really have a right to complain, does it?
file: str = 'file'


def read_obj(cfile: str) -> [dict]:
    if not exists(cfile):
        die('Failed to read keycap file "%s"' % cfile)
    rawCap: [str]
    if 'cfile' == '-':
        rawCap = stdin.readlines()
    else:
        with fopen(cfile, 'r') as f:
            rawCap = f.readlines()
    return parse_cap(rawCap)


def parse_cap(rawCap: [str]) -> [[str, int, int, [[str, list]]]]:
    robj: [[str]] = list(map(lambda l: l.strip().split(' '), rawCap))
    currGrpName: str = 'DEFAULT_GROUP'
    currGrpData: [[str, list]] = []
    obj: [[str, int, [[str, list]]]] = []
    currTotVertices: int = 0
    groupTotVertices: int = 0
    for line in robj:
        if line[0] == 'g':
            printi('Parsing group', currGrpName)
            # Handle the old group
            if currGrpName is not None:
                obj.append((currGrpName, currTotVertices, groupTotVertices,
                            currGrpData))
            groupTotVertices: int = 0
            # New group
            currGrpName = ' '.join(line[1:])
            currGrpData = []
        elif line[0] == 'v':
            # Parse vertex
            currGrpData.append((line[0], list(map(float, line[1:]))))
            currTotVertices += 1
            groupTotVertices += 1
        #  elif line[0] == 'f':
            #  # Parse face
            #  currGrpData.append(
                #  (line[0],
                 #  list(map(lambda p: list(map(int, p.split('/'))), line[1:]))))
        else:
            # Store text, don't handle
            currGrpData.append((line[0], line[1:]))
    if currGrpData != {}:
        obj.append(
            (currGrpName, currTotVertices, groupTotVertices, currGrpData))
    return obj


def write_obj(fname: str, data: [[str, int, int, [[str, list]]]]):
    if fname == '-':
        write_obj_to_file(data, stdout)
    else:
        with open(fname, 'w+') as f:
            write_obj_to_file(data, f)


def write_obj_to_file(obj: [[str, int, int, [[str, list]]]], f: file) -> str:
    for gn, _, _, gd in obj:
        print('g %s' % gn, file=f)
        print('o %s' % gn, file=f)
        for t, d in gd:
            #  if t == 'f':
                #  print('f',
                      #  ' '.join(
                          #  list(map(lambda t: '/'.join(list(map(str, t))), d))),
                      #  file=f)
            #  else:
            print(t, ' '.join(list(map(str, d))), file=f)
