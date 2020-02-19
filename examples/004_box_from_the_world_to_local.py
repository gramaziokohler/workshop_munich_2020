"""Example: Bring a box from the world coordinate system into another coordinate system.
"""
from compas.geometry import Frame
from compas.geometry import Box

# Box in the world coordinate system
frame = Frame([1, 0, 0], [-0.45, 0.1, 0.3], [1, 0, 0])
width, length, height = 1, 1, 1
box = Box(frame, width, length, height)

# Frame F representing a coordinate system
F = Frame([2, 2, 2], [0.978, 0.010, -0.210], [0.090, 0.882, 0.463])

# Represent box frame in frame F and construct new box
box_frame_transformed = F.to_world_coords(box.frame)
box_transformed = Box(box_frame_transformed, width, length, height)
print("Box frame transformed:", box_transformed.frame)

# drawing
from compas.datastructures import Mesh
from compas_rhino.artists import FrameArtist
from compas_rhino.artists import MeshArtist

FrameArtist(Frame.worldXY()).draw()
MeshArtist(Mesh.from_shape(box)).draw_faces()
FrameArtist(F).draw()
MeshArtist(Mesh.from_shape(box_transformed)).draw_faces()
