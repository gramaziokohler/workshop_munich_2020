"""Example: 'point in frame'

The simple example above shows how to use a frame as a coordinate system: 
Starting from a point `P` in the local (user-defined, relative) coordinate 
system of frame `F`, i.e. its position is relative to the origin and orientation
of `F`, we want to get the position `P_` of `P` in the global (world, absolute)
coordinate system.
"""
from compas.geometry import * 

point = Point(146.00, 150.00, 161.50)
xaxis = Vector(0.9767, 0.0010, -0.214)
yaxis = Vector(0.1002, 0.8818, 0.4609)

# coordinate system F
F = Frame(point, xaxis, yaxis)

# point in F (local coordinates)
P = Point(35., 35., 35.)

# point in global (world) coordinates
P_ = F.to_world_coords(P)
print(P_)
# check

P2 = F.to_local_coords(P_)
print(P2)