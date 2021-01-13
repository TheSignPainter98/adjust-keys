# Copyright (C) Edward Jones

from .log import printi
from .util import layout_is_wider_than_height
from bpy.types import MeshPolygon, Object
from mathutils import Matrix, Vector

def uv_unwrap(obj:Object, objw:Vector, partition_uv_by_face_direction:bool):
    #  # Ensure object mode
    #  origMode:str = context.object.mode
    #  if origMode != 'OBJECT':
        #  ops.object.mode_set(mode='OBJECT')

    # Project vertices into uv-space, assuming upper-left most point is at
    scale: float = uv_scale(objw)
    diag:[float] = diagonal(scale)
    wide_layout:bool = layout_is_wider_than_height(objw)
    printi('Scaling uv image by (%f, %f)' %(diag[0], diag[1]))
    for face in obj.data.polygons:
        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
            place_off:float = 1.0 if not partition_uv_by_face_direction or is_front_face(obj, face) else 0.5
            off:Vector = Vector((0.0, place_off)) if layout_is_wider_than_height else Vector((place_off, 0.0))
            obj.data.uv_layers.active.data[loop_idx].uv = scale @ obj.data.vertices[vert_idx].co.to_2d() + off

    #  # Reinstate previous mode
    #  if origMode != 'OBJECT':
        #  ops.object.mode_set(mode=origMode)


# Assume that the top left-most point occupied space is at (0,0)
def uv_scale(kbw:Vector) -> Matrix:
    return Matrix.Scale(1.0 / kbw[layout_is_wider_than_height(kbw)], 2)

def is_front_face(o:Object, f:MeshPolygon) -> bool:
    return max(map(lambda vi: o.data.vertices[vi].normal @ Vector((0.0, 1.0, 0.0)), f.vertices)) >= 0.0

# Assumes square matrix
def diagonal(m:Matrix) -> [float]:
    return [ m[i][i] for i in range(0, len(m[0])) ]
