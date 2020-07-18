# Copyright (C) Edward Jones
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

# Ensure blend location is on the python path
import bpy
from sys import path as ppath
from os.path import dirname
curr_dir:str = dirname(bpy.data.filepath)
if curr_dir not in ppath:
    ppath.append(curr_dir)

from adjustcaps import adjust_caps, get_caps
from adjustcaps_args import parse_args
from argparse import Namespace
from log import init_logging, printi
from obj_io import write_obj
from os import makedirs
from os.path import exists, join
from positions import translate_to_origin
from sys import argv, exit


def main(args: [str]) -> int:
    pargs: Namespace = parse_args(args)

    if pargs.move_to_origin:
        init_logging(pargs.verbosity)
        caps:[dict] = get_caps(pargs.cap_dir)
        if not exists(pargs.output_dir):
            printi('Making non-existent directory "%s"' % pargs.output_dir)
            makedirs(pargs.output_dir, exist_ok=True)
        for cap in caps:
            translate_to_origin(cap['cap-obj'])
            write_obj(join(pargs.output_dir, cap['cap-name'] + '.obj'), cap['cap-obj'])
    else:
        if not exists(pargs.output_dir):
            printi('Making non-existent directory "%s"' % pargs.output_dir)
            makedirs(pargs.output_dir, exist_ok=True)
        mfnames: [str] = adjust_caps(pargs.verbosity, pargs.unit_length, pargs.x_offset,
                    pargs.y_offset, pargs.plane, pargs.profile_file,
                    pargs.cap_dir, pargs.output_dir, pargs.layout_file,
                    pargs.layout_row_profile_file)

        #  seens:dict = {}
        #  for n,m in models:
            #  if n not in seens.keys():
                #  seens[n] = 1
            #  else:
                #  seens[n] += 1
            #  oname:str = join(pargs.output_dir, 'capmodel-' + n + ('-' + str(seens[n]) if seens[n] > 1 else '') + '.obj')
            #  printi('Outputting to "%s"' % oname)
            #  write_obj(oname, m)
        print(mfnames)
        for mfname in mfnames:
            bpy.ops.import_scene.obj(filepath=mfname)

    return 0

if __name__ == '__main__':
    try:
        exit(main(argv))
    except KeyboardInterrupt:
        exit(1)
