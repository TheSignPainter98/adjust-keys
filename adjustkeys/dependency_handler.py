# Copyright (C) Edward Jones

from .path import adjustkeys_path
from ensurepip import bootstrap as bootstrap_pip
from importlib import import_module, invalidate_caches
from importlib.util import find_spec
from os import _Environ, environ, makedirs
from os.path import dirname, exists, join
from subprocess import CalledProcessError, check_output, run
from sys import path

# Get the path to the python binary in use
python_bin_path:str = None
from bpy.app import version as bpy_version
if bpy_version >= (2, 91, 0):
    from sys import executable as python_bin_path
else:
    from bpy.app import binary_path_python as python_bin_path

pip:[str] = [python_bin_path, '-m', 'pip']
dependency_install_dir:str = join(dirname(__file__), 'site-packages')

def ensure_pip():
    try:
        run(pip + ['--version'], check=True)
    except CalledProcessError:
        bootstrap_pip()
        environ.pop('PIP_REQ_TRACKER', None)

def push_dependency_path():
    if dependency_install_dir not in path:
        path.append(dependency_install_dir)

def pop_dependency_path():
    if dependency_install_dir in path:
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

    if not exists(dependency_install_dir):
        makedirs(dependency_install_dir)
    run(pip + ['install', '--target', dependency_install_dir, '--upgrade', '--force-reinstall', pkg_name], env=environ)

    if prev_python_user_base is not None:
        environ['PYTHONUSERBASE'] = prev_python_user_base
    if prev_pip_target is not None:
        environ['PIP_TARGET'] = prev_pip_target

    # Invalidate the finder caches as a module has been installed since the python interpreter began
    invalidate_caches()

    # Check that the import worked.
    test_module_available(mod_name)

def test_module_available(mod_name:str):
    __import__(mod_name) # Import the module without adding it to the current namespace
