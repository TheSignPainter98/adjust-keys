# Copyright (C) Edward Jones

from .exceptions import AdjustKeysException
from argparse import Namespace
from sys import argv, stderr

fatal_warnings: bool = False
verbosity: int = 0
warnings:[[tuple,dict]] = []


##
# @brief Initialise logging, should be called before any logging is to take place
#
# @param verbose_in:bool Whether to output verbosely
# @param quiet_in:bool Whether to output quietly
#
# @return Nothing
def init_logging(pargs:Namespace):
    global fatal_warnings
    global verbosity
    fatal_warnings = pargs.fatal_warnings
    verbosity = pargs.verbosity
    warnings = []


##
# @brief Print all of the stored warnings
#
# @return The number of warnings printed
def print_warnings() -> int:
    global warnings
    for args,kwargs in warnings:
        print(*args, file=stderr, **kwargs)
    num_warnings:int = len(warnings)
    warnings = []
    return num_warnings

##
# @brief Write a message to stderr and raise an exception
#
# @param args Message things
# @param kwargs key-value message things
#
# @return Nothing
def die(*args, **kwargs):
    raise AdjustKeysException(' '.join(list(map(str, args))))


##
# @brief Output information to stderr
#
# @param args Message things
# @param kwargs More message things
#
# @return Nothing
def printi(*args, **kwargs):
    if verbosity >= 2:
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
    if fatal_warnings:
        die(*args, **kwargs)
    if verbosity >= 1:
        warnings.append((['WARNING:'] + list(args), kwargs))
