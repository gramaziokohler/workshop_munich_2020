import os
import time
import json
from compas.geometry import Frame
from compas.geometry import Transformation
from compas_fab.backends import RosClient
from compas_fab.robots import PlanningScene
from compas_fab.robots import CollisionMesh

from assembly_information_model.assembly import Element

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

# load settings (shared by GH)
settings_file = os.path.join(DATA, "settings.json")
with open(settings_file, 'r') as f:
    data = json.load(f)

# create Element and move it to picking frame
element0 = Element.from_data(data['element0'])
picking_frame = Frame.from_data(data['picking_frame'])
element0.transform(Transformation.from_frame_to_frame(element0._tool_frame, picking_frame))

with RosClient('localhost') as client:
    robot = client.load_robot()
    scene = PlanningScene(robot)

    # create a CollisionMesh from the element and add it to the scene
    brick = CollisionMesh(element0.mesh, 'brick_wall')
    scene.append_collision_mesh(brick)

    time.sleep(2)

    # Remove elements from scene
    # scene.remove_collision_mesh(brick.id)
    # time.sleep(1)
