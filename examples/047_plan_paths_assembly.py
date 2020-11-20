import os
import json
from compas.geometry import Vector
from compas.geometry import Frame
from compas.geometry import Transformation
from compas.datastructures import Mesh
from compas_fab.backends import RosClient
from compas_fab.robots import PlanningScene
from compas_fab.robots import Configuration
from compas_fab.robots import Tool
from compas_fab.robots import AttachedCollisionMesh
from compas_fab.robots import CollisionMesh
from compas_fab.backends import BackendError

from assembly_information_model.assembly import Assembly
from assembly_information_model.assembly import Element

from helpers import plan_picking_motion
from helpers import plan_moving_and_placing_motion

# Path settings
HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
PATH_TO = os.path.join(DATA, os.path.splitext(
    os.path.basename(__file__))[0] + ".json")

LOAD_FROM_EXISTING = False

# create tool from json
filepath = os.path.join(DATA, "airpick.json")
tool = Tool.from_json(filepath)
# load settings (shared by GH)
settings_file = os.path.join(DATA, "settings.json")
with open(settings_file, 'r') as f:
    data = json.load(f)
# load Element
element0 = Element.from_data(data['element0'])
# picking frame
picking_frame = Frame.from_data(data['picking_frame'])
picking_configuration = Configuration.from_data(data['picking_configuration'])
# little tolerance to not 'crash' into collision objects
tolerance_vector = Vector.from_data(data['tolerance_vector'])
safelevel_vector = Vector.from_data(data['safelevel_vector'])
safelevel_picking_frame = picking_frame.copy()
safelevel_picking_frame.point += safelevel_vector
picking_frame.point += tolerance_vector
# collision_meshes
scene_collision_meshes = [CollisionMesh(Mesh.from_data(m), name) for m, name in
                          zip(data['collision_meshes'], data['collision_names'])]

# load assembly from file or from existing if calculation failed at one point...
filepath = os.path.join(DATA, "assembly.json")

if LOAD_FROM_EXISTING and os.path.isfile(PATH_TO):
    assembly = Assembly.from_json(PATH_TO)
else:
    assembly = Assembly.from_json(filepath)

# create an attached collision mesh to be attached to the robot's end effector.
T = Transformation.from_frame_to_frame(element0._tool_frame, tool.frame)
element0_tool0 = element0.transformed(T)
attached_element_mesh = AttachedCollisionMesh(
    CollisionMesh(element0_tool0.mesh, 'element'), 'ee_link')

# ==============================================================================
# From here on: fill in code, whereever you see this dots ...

# NOTE: If you run Docker Toolbox, change `localhost` to `192.168.99.100`
with RosClient('localhost') as client:

    robot = client.load_robot()
    scene = PlanningScene(robot)
    robot.attach_tool(tool)

    # 1. Add a collison mesh to the planning scene: floor, desk, etc.
    for cm in scene_collision_meshes:
        scene.add_collision_mesh(cm)
    if not LOAD_FROM_EXISTING:
        scene.remove_collision_mesh('assembly')

    # 2. Compute picking trajectory
    picking_trajectory = plan_picking_motion(robot, picking_frame,
                                             safelevel_picking_frame,
                                             picking_configuration,
                                             attached_element_mesh)

    # 3. Save the last configuration from that trajectory as new
    # start_configuration
    start_configuration = Configuration(picking_trajectory.points[-1].values, picking_trajectory.points[-1].types)

    sequence = [key for key in assembly.network.nodes()]
    sequence = list(range(10))
    print(sequence)
    exclude_keys = [vkey for vkey in assembly.network.nodes_where({'is_planned': True})]
    sequence = [k for k in sequence if k not in exclude_keys]
    print(sequence)

    for key in sequence:
        print("=" * 30 + "\nCalculating path for element with key %d." % key)

        element = assembly.element(key)

        # 4. Create an attached collision mesh and attach it to the robot's end
        # effector.
        T = Transformation.from_frame_to_frame(element._tool_frame, tool.frame)
        element_tool0 = element.transformed(T)
        ee_link_name = robot.get_end_effector_link_name()
        attached_element_mesh = AttachedCollisionMesh(CollisionMesh(element_tool0.mesh, 'element'), ee_link_name)
        # add the collision mesh to the scene
        scene.add_attached_collision_mesh(attached_element_mesh)

        # 5. Calculate moving_ and placing trajectories
        for i in range(10):
            try:
                moving_trajectory, placing_trajectory = plan_moving_and_placing_motion(robot,
                                                                                       element,
                                                                                       start_configuration,
                                                                                       tolerance_vector,
                                                                                       safelevel_vector,
                                                                                       attached_element_mesh)
                
                if placing_trajectory.fraction != 1:
                    raise BackendError("Cartesian path not working")
                else:
                    break

            except BackendError:
                print("Trying the %d. time" % (i + 2))
                continue
        else:
            raise BackendError("NOT FOUND")

        # 6. Add the element to the planning scene
        cm = CollisionMesh(element.mesh, "assembly")
        scene.append_collision_mesh(cm)

        # 7. Add calculated trajectories to element and set to 'planned'
        element.trajectory = [picking_trajectory,
                              moving_trajectory, placing_trajectory]
        assembly.network.node_attribute(key, 'is_planned', True)

        # 8. Save assembly to json after every placed element
        assembly.to_json(PATH_TO, pretty=True)
