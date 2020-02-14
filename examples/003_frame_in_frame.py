"""Example: 'frame in frame'
"""
from compas.geometry import * 

# coordinate system F0
point = Point(146.00, 150.00, 161.50)
xaxis = Vector(0.9767, 0.0010, -0.214)
yaxis = Vector(0.1002, 0.8818, 0.4609)
F0 = Frame(point, xaxis, yaxis)

# frame F in F0 (local coordinates)
point = Point(35., 35., 35.)
xaxis = Vector(0.604, 0.430, 0.671)
yaxis = Vector(-0.631, 0.772, 0.074)
F = Frame(point, xaxis, yaxis)

# frame in global (world) coordinate system
F_wcf = F0.to_world_coords(F)
print(F_wcf)

# check
F2 = F0.to_local_coords(F_wcf)
print(F2)
print(F == F2)