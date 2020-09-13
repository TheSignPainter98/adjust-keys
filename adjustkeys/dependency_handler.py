# Copyright (C) Edward Jones

from .path import adjustkeys_path
from bpy.app import binary_path_python
from ensurepip import bootstrap as bootstrap_pip
from importlib import import_module as import_mod
from importlib.util import find_spec
from os import _Environ, environ, makedirs
from os.path import dirname, exists, join
#  from pip import main as pip
from subprocess import CalledProcessError, check_output, run
from sys import path

pip:[str] = [binary_path_python, '-m', 'pip']
#  pip:[str] = [join(dirname(binary_path_python), 'pip3')] # Windows version doesn't seem to ship with the PIP binary... hooray...
dependency_path_modified:bool = False
dependency_install_dir:str = join(dirname(__file__), 'site-packages')

def ensure_pip():
    try:
        run(pip + ['--version'], check=True)
    except CalledProcessError:
        bootstrap_pip()
        environ.pop('PIP_REQ_TRACKER', None)

def push_dependency_path():
    if dependency_install_dir not in path:
        dependency_path_modified = True
        path.append(dependency_install_dir)

def pop_dependency_path():
    if dependency_path_modified:
        del path[path.index(dependency_install_dir)]

def install_module(mod_name:str, pkg_name:str=None, global_name:str=None):
    if pkg_name is None:
        pkg_name = mod_name
    if global_name is None:
        global_name = mod_name

    prev_python_user_base:str = environ.pop('PYTHONUSERBASE', None)
    prev_pip_target:str = environ.pop('PIP_TARGET', None)
    environ['PYTHONUSERBASE'] = dependency_install_dir
    environ['PIP_TARGET'] = dependency_install_dir

    # '--force-reinstall',
    if not exists(dependency_install_dir):
        makedirs(dependency_install_dir)
    run(pip + ['install', '--target', dependency_install_dir, '--upgrade', '--force-reinstall', pkg_name], env=environ)

    if prev_python_user_base is not None:
        environ['PYTHONUSERBASE'] = prev_python_user_base
    if prev_pip_target is not None:
        environ['PIP_TARGET'] = prev_pip_target

    # Check that the import worked.
    push_dependency_path()
    import_module(mod_name, global_name)
    pop_dependency_path()

def import_module(mod_name:str, global_name:str=None):
    if global_name is None:
        global_name = mod_name
    globals()[global_name] = import_mod(mod_name)
