# Copyright (C) Edward Jones

from .path import adjustkeys_path
from bpy.app import binary_path_python
from ensurepip import bootstrap as bootstrap_pip
from importlib import import_module as import_mod
from importlib.util import find_spec
from os import environ
from os.path import exists, join
#  from pip import main as pip
from subprocess import CalledProcessError, check_output, run

pip:[str] = [binary_path_python, '-m', 'pip']

#  have_run_dependency_handler:bool = False

#  def handle_missing_dependencies():
    #  # Don't run the dependency handler multiple times in the same session
    #  global have_run_dependency_handler
    #  if have_run_dependency_handler:
        #  return
    #  have_run_dependency_handler = True

    #  # Get dependency list
    #  requirements_file:str = join(adjustkeys_path, 'requirements.txt')
    #  if not exists(requirements_file):
        #  return

    #  ensure_pip()

    #  check_output(pip + ['install', '-r', requirements_file])


    #  #  binary_path_python:str
    #  #  if find_spec('bpy') is None:
        #  #  from sys import executable
        #  #  binary_path_python = executable
    #  #  else:
        #  #  from bpy.app import binary_path_python as bpp
        #  #  binary_path_python = bpp

    #  #  # Ensure that pip is installed
    #  #  (ensurePipProc, _) = run_proc([binary_path_python, '-m', 'ensurepip'])
    #  #  if ensurePipProc.returncode:
        #  #  from .exceptions import AdjustKeysException
        #  #  raise AdjustKeysException('Something went wrong when ensuring pip was installed, see console output for more details')

    #  #  # Install any missing packages
    #  #  (pipInstallProc, _) = run_proc([binary_path_python, '-m', 'pip', 'install', '-r', requirements_file])
    #  #  if pipInstallProc.returncode:
        #  #  from .exceptions import AdjustKeysException
        #  #  raise AdjustKeysException('Something went wrong when getting the list of installed packages, see pip output for more details')
    #  #  print('Successfully installed adjustkeys any missing dependencies')

def ensure_pip():
    try:
        run(pip + ['--version'], check=True)
    except CalledProcessError:
        bootstrap_pip()
        environ.pop('PIP_REQ_TRACKER', None)

def install_module(mod_name:str, pkg_name:str=None, global_name:str=None):
    if pkg_name is None:
        pkg_name = mod_name
    if global_name is None:
        global_name = mod_name

    run(pip + ['install', pkg_name])

    import_module(mod_name, global_name)

def import_module(mod_name:str, global_name:str=None):
    if global_name is None:
        global_name = mod_name
    globals()[global_name] = import_mod(mod_name)
