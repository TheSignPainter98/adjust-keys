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

from adjustcaps import adjust_caps
from adjustcaps_args import parse_args
from argparse import Namespace
from sys import argv, exit


def main(args: [str]) -> int:
    pargs: Namespace = parse_args(args)
    kbobj: str = adjust_caps(pargs.verbosity, pargs.unit_length,
                             pargs.global_x_offset, pargs.global_y_offset,
                             pargs.profile_file, pargs.cap_dir,
                             pargs.layout_file, pargs.layout_row_profile_file)

    if pargs.output_location == '-':
        print(kbobj)
    else:
        with open(pargs.output_location, 'w+') as f:
            print(kbobj, file=f)

    return 0


if __name__ == '__main__':
    exit(main(argv))
