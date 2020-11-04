import os
import json
import time
from compas.geometry import Frame
from compas.geometry import Transformation
from compas_fab.backends import RosClient
from compas_fab.robots import PlanningScene
from compas_fab.robots import CollisionMesh
from compas_fab.robots import AttachedCollisionMesh
from compas_fab.robots import Tool

import sys
sys.path.append(r"C:\Users\rustr\workspace\libraries\assembly_information_model\src")
from assembly_information_model.assembly import Element

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

# create tool from json
filepath = os.path.join(DATA, "vacuum_gripper.json")
tool = Tool.from_json(filepath)

# load settings (shared by GH)
settings_file = os.path.join(DATA, "settings.json")
with open(settings_file, 'r') as f:
    data = json.load(f)

# create Element and move it to target frame
element0 = Element.from_data(data['element0'])

# define picking frame
picking_frame = Frame.from_data(data['picking_frame'])

element0.transform(Transformation.from_frame_to_frame(element0._tool_frame, picking_frame))

# now we need to bring the element's mesh into the robot's tool0 frame
element0_tool0 = element0.copy()
T = Transformation.from_frame_to_frame(element0_tool0._tool_frame, tool.frame)
element0_tool0.transform(T)

with RosClient('localhost') as client:
    robot = client.load_robot()
    scene = PlanningScene(robot)

    # attach tool
    robot.attach_tool(tool)
    # add tool to scene
    scene.add_attached_tool()

    # create an attached collision mesh to the robot's end effector.
    ee_link_name = robot.get_end_effector_link_name()
    brick_acm = AttachedCollisionMesh(CollisionMesh(element0_tool0.mesh, 'brick'), ee_link_name)
    # add the collision mesh to the scene
    scene.add_attached_collision_mesh(brick_acm)

    time.sleep(2)

    # Remove tool and brick
    scene.remove_attached_collision_mesh(brick_acm.collision_mesh.id)
    scene.remove_collision_mesh(brick_acm.collision_mesh.id)

    scene.remove_attached_tool()
    scene.remove_collision_mesh(tool.name)
    robot.detach_tool()

    time.sleep(1)
