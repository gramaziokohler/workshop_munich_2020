import compas
from compas.datastructures import Mesh
from compas.geometry import Circle
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.geometry import Plane
from compas.geometry import Translation
from compas.robots import Joint
from compas.robots import RobotModel
from compas_fab.rhino import RobotArtist
from compas_fab.robots import Configuration

# create cylinder in yz plane
radius, length = 0.3, 5
cylinder = Cylinder(Circle(Plane([0, 0, 0], [1, 0, 0]), radius), length)
cylinder.transform(Translation([length / 2., 0, 0]))

# create robot
robot = RobotModel("robot", links=[], joints=[])

# add links
link0 = robot.add_link("world")
link1 = robot.add_link("link1", visual_mesh=Mesh.from_shape(cylinder))
link2 = robot.add_link("link2", visual_mesh=Mesh.from_shape(cylinder))

# add the joints between the links
axis = (0, 0, 1)
origin = Frame.worldXY()
robot.add_joint("joint1", Joint.CONTINUOUS, link0, link1, origin, axis)

origin = Frame((length, 0, 0), (1, 0, 0), (0, 1, 0))
robot.add_joint("joint2", Joint.CONTINUOUS, link1, link2, origin, axis)

print(robot)

if compas.IPY:
    artist = RobotArtist(robot, layer='COMPAS:RobotModel')
    artist.clear_layer()
    artist.draw_visual()
