# Copyright (C) Edward Jones

from .log import printi
from .lazy_import import LazyImport

Matrix:type = LazyImport('mathutils', 'Matrix')
MeshPolygon:type = LazyImport('bpy', 'types', 'MexhPolygon')
Object:type = LazyImport('bpy', 'types', 'Object')
Vector:type = LazyImport('mathutils', 'Vector')

def uv_unwrap(obj:Object, objw:Vector, partition_uv_by_face_direction:bool):
    #  # Ensure object mode
    #  origMode:str = context.object.mode
    #  if origMode != 'OBJECT':
        #  ops.object.mode_set(mode='OBJECT')

    # Project vertices into uv-space, assuming upper-left most point is at
    scale: float = uv_scale(partition_uv_by_face_direction, objw)
    diag:[float] = diagonal(scale)
    printi('Scaling uv image to fill space (%fx, %fy)' %(diag[0], diag[1]))
    for face in obj.data.polygons:
        front_face:bool = is_front_face(obj, face)
        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
            place_off:float = 1.0 if not partition_uv_by_face_direction or front_face else 0.5
            off:Vector = Vector((0.0, place_off))
            obj.data.uv_layers.active.data[loop_idx].uv = scale @ obj.data.vertices[vert_idx].co.to_2d() + off

    #  # Reinstate previous mode
    #  if origMode != 'OBJECT':
        #  ops.object.mode_set(mode=origMode)

    printi('Done scaling uv image')


# Assume that the top left-most point occupied space is at (0,0)
def uv_scale(partition_uv_by_face_direction:bool, kbw:Vector) -> Matrix:
    # Matrix to scale to the space [0,1]^2
    uv_scale_mat:Matrix = Matrix.Diagonal(kbw).inverted()

    # Halve the second componenet if partitioning
    if partition_uv_by_face_direction:
        uv_scale_mat @= Matrix.Diagonal((1, 0.5))

    return uv_scale_mat

def is_front_face(o:Object, f:MeshPolygon) -> bool:
    return max(map(lambda vi: o.data.vertices[vi].normal @ Vector((0.0, 1.0, 0.0)), f.vertices)) >= 0.0

# Assumes square matrix
def diagonal(m:Matrix) -> [float]:
    return [ m[i][i] for i in range(0, len(m[0])) ]
