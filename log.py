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

from sys import argv, stderr

verbose:bool = False
quiet:bool = False

def init_logging(verbose_in:bool, quiet_in:bool):
    global quiet, verbose
    if verbose_in and quiet_in:
        die("Please don't try to output both verbosely and quietly, it doesn't make any sense")
    verbose = verbose_in
    quiet = quiet_in

def die(*args, **kwargs):
    printe(*args, **kwargs)
    exit(1)

def printi(*args, **kwargs):
    if verbose:
        print(*args, file=stderr, **kwargs)

def printe(*args, **kwargs):
    print(f'{argv[0]}:', *args, file=stderr, **kwargs)

def printw(*args, **kwargs):
    if not quiet:
        print(f'{argv[0]}: WARNING:', *args, **kwargs)
