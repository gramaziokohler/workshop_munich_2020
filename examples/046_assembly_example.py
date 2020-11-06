
import os
import json
import math

from compas.geometry import Frame
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Transformation
from compas.geometry import Rotation
from compas.geometry import Translation

from assembly_information_model.assembly import Assembly
from assembly_information_model.assembly import Element

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

# load settings (shared by GH)
settings_file = os.path.join(DATA, "settings.json")
with open(settings_file, 'r') as f:
    data = json.load(f)

# create Element and move it to picking frame
element0 = Element.from_data(data['element0'])

# initialize an empty assembly class
assembly = Assembly()

cf = Frame(Point(0.4, 0.4, 0.), Vector(1., 0., 0.), Vector(0., 1., 0.))

for i in range(25):  # loop through the number of layers i

    axis = cf.zaxis
    angle = math.radians(i*3)

    # Calculates a ``Rotation`` from a rotation axis and an angle and an optional point of rotation.
    R = Rotation.from_axis_and_angle(axis, angle, point=cf.point)
    T = Translation.from_vector([0, 0, 0.005*i])

    cft = cf.transformed(R * T)  # transforms the origin plane

    if i % 2 == 0:
        R = Rotation.from_axis_and_angle(
            cft.zaxis, math.radians(90), point=cft.point)
        cft = cft.transformed(R)

    add = math.sin(i/5)*0.015
    # print(add)

    o1 = cft.point + cft.yaxis*(0.075+add)
    o2 = cft.point - cft.yaxis*(0.075+add)

    f1 = Frame(o1, cft.xaxis, cft.yaxis)
    f2 = Frame(o2, cft.xaxis, cft.yaxis)

    T1 = Transformation.from_frame_to_frame(Frame.worldXY(), f1)
    T2 = Transformation.from_frame_to_frame(Frame.worldXY(), f2)

    # create new instances of the element
    # returns a deep copy of the initial element at the new location of the frame
    new_elem_1 = element0.transformed(T1)
    new_elem_2 = element0.transformed(T2)

    assembly.add_element(new_elem_1)
    assembly.add_element(new_elem_2)

assembly.to_json(os.path.join(DATA, "assembly.json"), pretty=True)
