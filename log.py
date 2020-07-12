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

verbosity: int = 0


##
# @brief Initialise logging, should be called before any logging is to take place
#
# @param verbose_in:bool Whether to output verbosely
# @param quiet_in:bool Whether to output quietly
#
# @return Nothing
def init_logging(verbosity_in: bool):
    global verbosity
    verbosity = verbosity_in


##
# @brief Write a message to stderr and exit
#
# @param args Message things
# @param kwargs key-value message things
#
# @return Nothing
def die(*args, **kwargs):
    printe(*args, **kwargs)
    exit(1)


##
# @brief Output information to stderr
#
# @param args Message things
# @param kwargs More message things
#
# @return Nothing
def printi(*args, **kwargs):
    if verbosity >= 1:
        print(*args, file=stderr, **kwargs)


##
# @brief Output an error to stderr
#
# @param args Message things
# @param kwargs More message things
#
# @return Nothing
def printe(*args, **kwargs):
    print(f'{argv[0]}:', *args, file=stderr, **kwargs)


##
# @brief Output a warning on stderr
#
# @param args Message things
# @param kwargs More message things
#
# @return Nothing
def printw(*args, **kwargs):
    if verbosity >= 0:
        print(f'{argv[0]}: WARNING:', *args, file=stderr, **kwargs)
