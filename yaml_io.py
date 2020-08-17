# Copyright (C) Edward Jones

from log import die, printi
from os.path import exists
from path import fexists, fopen
from sys import stdin
from yaml import dump, safe_load


##
# @brief Read yaml from a given file or '-' for stdin. Exits on error
#
# @param fname:str Name of the file to use
#
# @return The data present in file fname
def read_yaml(fname: str) -> dict:
    if fname == '-':
        printi(
            'Reading %s from stdin, please either type something or redirect a file in here'
            % fname)
        return safe_load(stdin)
    else:
        if fexists(fname):
            with fopen(fname, 'Could not find file "%s"' % fname, 'Multiple files (%%d) named "%s" found: %%s' % fname, 'r', encoding='utf-8') as f:
                return safe_load(f)
        else:
            die('Failed to read file "%s"' % fname)


##
# @brief Write a dictionary to a given file, or '-' for stdout
#
# @param fname:str Name of file to write data into or '-' for stdout
# @param data:dict Data to write
#
# @return Nothing
def write_yaml(fname: str, data: dict):
    if fname == '-':
        print(dump(data), end='')
    else:
        with open(fname, 'w+', encoding='utf-8') as f:
            print(dump(data), file=f, end='')
