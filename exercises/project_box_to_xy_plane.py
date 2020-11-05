from compas.geometry import Frame
from compas.geometry import Plane
from compas.geometry import Projection
from compas.geometry import Transformation
from compas.geometry import Box
from compas_rhino.artists import BoxArtist
from compas_rhino.artists import MeshArtist
from compas.datastructures import Mesh

# Box in the world coordinate system
frame = Frame([1, 0, 0], [-0.45, 0.1, 0.3], [1, 0, 0])
width, length, height = 1, 1, 1
box = Box(frame, width, length, height)

# Frame F representing a coordinate system
F = Frame([2, 2, 2], [0.978, 0.010, -0.210], [0.090, 0.882, 0.463])

# Get transformation between frames and apply transformation on box.
T = Transformation.from_frame_to_frame(Frame.worldXY(), F)
box_transformed = box.transformed(T)

# make Mesh from box
mesh_transformed = Mesh.from_shape(box_transformed)

# create Projection
P = Projection.from_plane_and_direction(Plane((0, 0, 0), (0, 0, 1)), (3, 5, 5))
P = Projection.from_plane(Plane((0, 0, 0), (0, 0, 1)))
P = Projection.from_plane_and_point(Plane((0, 0, 0), (0, 0, 1)), (3, 5, 5))

# apply transformation on mesh
mesh_projected = mesh_transformed.transformed(P)

# create artists
artist1 = BoxArtist(box_transformed)
artist2 = MeshArtist(mesh_projected)

# draw
artist1.draw()
artist2.draw()
