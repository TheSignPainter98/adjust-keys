# Copyright (C) Edward Jones

def handle_missing_dependencies():
    # Get dependency list
    from importlib.util import find_spec
    from os.path import exists, join
    from path import adjustkeys_path
    requirements_file:str = join(adjustkeys_path, 'requirements.txt')
    if not exists(requirements_file):
        return
    from subprocess import PIPE, Popen
    binary_path_python:str
    if find_spec('bpy') is None:
        from sys import executable
        binary_path_python = executable
    else:
        from bpy.app import binary_path_python as bpp
        binary_path_python = bpp

    # Get installed packages
    pipListProc:Popen = Popen([binary_path_python, '-m', 'pip', 'list'], stdout=PIPE, stderr=PIPE)
    o:tuple = pipListProc.communicate()
    pstdout:str = o[0].decode()
    pstderr:str = o[1].decode()
    if pipListProc.returncode or pstderr:
        from exceptions import AdjustKeysException
        raise AdjustKeysException(pstderr)
    installed_packages:[str] = list(map(lambda l: l.split(' ')[0], filter(lambda l: l, pstdout.split('\n'))))[2:]

    # Get required packages
    req_lines:[str]
    with open(requirements_file, 'r') as rf:
        req_lines = rf.readlines()
    reqs:[str] = list(map(lambda l: l.split('==')[0], req_lines))

    # Compute missing packages
    missing_packages:[str] = [ pkg for pkg in reqs if pkg not in installed_packages ]

    # Install any missing packages
    if missing_packages != []:
        pipInstallProc:Popen = Popen([binary_path_python, '-m', 'pip', '-r', requirements_file], stdout=PIPE, stderr=PIPE)
        o:tuple = pipInstallProc.communicate()
        pstdout2:str = o[0].decode()
        pstderr2:str = o[1].decode()
        if pipInstallProc.returncode or pstderr2:
            from exceptions import AdjustKeysException
            raise AdjustKeysException(pstderr2)
        print('Successfully installed adjustkeys dependencies')

