# Copyright (C) Edward Jones

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
