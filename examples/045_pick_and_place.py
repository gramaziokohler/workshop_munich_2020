import os
import math
import time
import json
from compas.geometry import Vector
from compas.geometry import Frame
from compas.geometry import Transformation
from compas_fab.backends import RosClient
from compas_fab.robots import PlanningScene
from compas_fab.robots import Configuration
from compas_fab.robots import Tool
from compas_fab.robots import AttachedCollisionMesh
from compas_fab.robots import CollisionMesh
#from assembly import Element
#from assembly import Assembly

from assembly_information_model.assembly import Element, Assembly

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
PATH_TO = os.path.join(DATA, os.path.splitext(os.path.basename(__file__))[0] + ".json")
print(PATH_TO)


# create tool from json
filepath = os.path.join(DATA, "vacuum_gripper.json")
tool = Tool.from_json(filepath)

# load settings (shared by GH)
settings_file = os.path.join(DATA, "settings.json")
with open(settings_file, 'r') as f:
    data = json.load(f)

# create Element
element0 = Element.from_data(data['element0'])
# picking frame
picking_frame = Frame.from_data(data['picking_frame'])
# little tolerance to not 'crash' into collision objects
tolerance_vector = Vector.from_data(data['tolerance_vector'])
savelevel_vector = Vector.from_data(data['savelevel_vector'])

# define target frame
target_frame = Frame((0.325, 0.400, 0.006), (0.000, 1.000, 0.000), (-1.000, 0.000, 0.000))
target_frame.point += tolerance_vector

# create Assembly with element at target_frame
assembly = Assembly()
T = Transformation.from_frame_to_frame(element0.frame, target_frame)
assembly.add_element(element0.transformed(T))

# Bring the element's mesh into the robot's tool0 frame
element_tool0 = element0.copy()
T = Transformation.from_frame_to_frame(element_tool0._tool_frame, tool.frame)
element_tool0.transform(T)

# define picking_configuration
picking_configuration = Configuration.from_data(data['picking_configuration'])

# define picking frame
picking_frame = Frame.from_data(data['picking_frame'])
picking_frame.point += tolerance_vector

# define savelevel frames 'above' the picking- and target frames
savelevel_picking_frame = picking_frame.copy()
savelevel_picking_frame.point += savelevel_vector
savelevel_target_frame = target_frame.copy()
savelevel_target_frame.point += savelevel_vector

# settings for plan_motion
tolerance_position = 0.001
tolerance_axes = [math.radians(1)] * 3

with RosClient('localhost') as client:
    robot = client.load_robot()
    scene = PlanningScene(robot)

    scene.remove_collision_mesh('brick_wall')

    # attach tool
    robot.attach_tool(tool)
    # add tool to scene
    scene.add_attached_tool()

    # create an attached collision mesh to the robot's end effector.
    ee_link_name = robot.get_end_effector_link_name()
    brick_acm = AttachedCollisionMesh(CollisionMesh(element_tool0.mesh, 'brick'), ee_link_name)
    # add the collision mesh to the scene
    scene.add_attached_collision_mesh(brick_acm)

    # ==========================================================================
    # 1. Calculate a cartesian motion from the picking frame to the savelevel_picking_frame
    frames = [picking_frame, savelevel_picking_frame]

    start_configuration = picking_configuration
    trajectory1 = robot.plan_cartesian_motion(robot.from_tcf_to_t0cf(frames),
                                              start_configuration,
                                              options=dict(
                                                  max_step=0.01,
                                                  attached_collision_meshes=[brick_acm],
                                              ))
    assert(trajectory1.fraction == 1.)

    # ==========================================================================
    key = 0
    element = assembly.element(key)

    # 2. Calulate a free-space motion to the savelevel_target_frame
    savelevel_target_frame_tool0 = robot.from_tcf_to_t0cf(
        [savelevel_target_frame])[0]
    goal_constraints = robot.constraints_from_frame(savelevel_target_frame_tool0,
                                                    tolerance_position,
                                                    tolerance_axes)

    # as start configuration take last trajectory's end configuration
    start_configuration = Configuration(trajectory1.points[-1].values, trajectory1.points[-1].types)
    trajectory2 = robot.plan_motion(goal_constraints,
                                    start_configuration,
                                    options=dict(
                                        planner_id='RRT',
                                        attached_collision_meshes=[brick_acm]
                                    ))

    # 3. Calculate a cartesian motion to the target_frame
    frames = [savelevel_target_frame, target_frame]
    # as start configuration take last trajectory's end configuration
    start_configuration = Configuration(trajectory2.points[-1].values, trajectory2.points[-1].types)
    trajectory3 = robot.plan_cartesian_motion(robot.from_tcf_to_t0cf(frames),
                                              start_configuration,
                                              options=dict(
                                                max_step=0.01,
                                                attached_collision_meshes=[brick_acm]
                                              ))
    print(trajectory3.fraction)
    assert(trajectory3.fraction == 1.)

    # 4. Add the brick to the planning scene
    brick = CollisionMesh(element.mesh, 'brick_wall')
    scene.append_collision_mesh(brick)

    # 5. Add trajectories to element and set to 'planned'
    element.trajectory = trajectory1.points + trajectory2.points + trajectory3.points
    assembly.network.set_vertex_attribute(key, 'is_planned', True)
    # ==========================================================================

    time.sleep(1)

# 6. Save assembly to json
assembly.to_json(PATH_TO)
