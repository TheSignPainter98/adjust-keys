# Copyright (C) Edward Jones

from importlib.util import find_spec

blender_is_available:bool = None

def blender_available() -> bool:
    global blender_is_available
    if blender_is_available is None:
        blender_is_available = find_spec('bpy') is not None
    return blender_is_available
