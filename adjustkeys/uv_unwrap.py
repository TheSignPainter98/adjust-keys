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
    scale: Matrix = uv_scale(partition_uv_by_face_direction, objw)
    scale_x:float = scale[0][0]
    scale_y:float = scale[1][1]
    diag:[float] = diagonal(scale)
    data = obj.data.uv_layers.active.data
    vertices = obj.data.vertices

    printi('Projecting uv map...')
    for face in obj.data.polygons:
        off:Vector = Vector((0.0, 1.0))
        front_face:bool
        if partition_uv_by_face_direction:
            front_face = is_front_face(vertices, face)
            off.y = 0.5 if front_face else 1.0
        for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
            #  data[loop_idx].uv = scale @ vertices[vert_idx].co.to_2d() + off
            uv = data[loop_idx].uv
            co = vertices[vert_idx].co
            uv.x = scale_x * co.x + off.x
            uv.y = scale_y * co.y + off.y

    #  # Reinstate previous mode
    #  if origMode != 'OBJECT':
        #  ops.object.mode_set(mode=origMode)

    printi('Done projecting uv map')


# Assume that the top left-most point occupied space is at (0,0)
def uv_scale(partition_uv_by_face_direction:bool, kbw:Vector) -> Matrix:
    # Matrix to scale to the space [0,1]^2
    uv_scale_mat:Matrix = Matrix.Diagonal(kbw).inverted()

    # Halve the second componenet if partitioning
    if partition_uv_by_face_direction:
        uv_scale_mat @= Matrix.Diagonal((1, 0.5))

    return uv_scale_mat

def is_front_face(vertices:list, f:MeshPolygon) -> bool:
    return max(map(lambda vi: vertices[vi].normal @ Vector((0.0, 1.0, 0.0)), f.vertices)) >= 0.0

# Assumes square matrix
def diagonal(m:Matrix) -> [float]:
    return [ m[i][i] for i in range(0, len(m[0])) ]
