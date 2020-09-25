# Copyright (C) Edward Jones

from .blender_available import blender_available
Collection:type = None
if blender_available():
    from bpy import context, data
    from bpy.types import Collection

def make_collection(collection_intended_name:str) -> Collection:
    i:int = 0
    col_name:str = collection_intended_name
    while col_name in data.collections:
        i += 1
        col_name = collection_intended_name + '-' + str(i)
    collection:Collection = data.collections.new(col_name)
    context.scene.collection.children.link(collection)
    return collection
