# Copyright (C) Edward Jones

from log import printe, printi
from os.path import exists
from sys import stdin
from yaml import dump, FullLoader, safe_load


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
        return safe_load(stdin, Loader=FullLoader)
    else:
        if exists(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                return safe_load(f)
        else:
            printe('Failed to read file "%s"' % fname)
            exit(1)


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
