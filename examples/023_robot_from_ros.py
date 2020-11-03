# Before running this example, make sure to run
# "docker compose up" on the docker-ur10e file
import compas
from compas.robots import RobotModel
from compas_fab.backends import RosClient
from compas_fab.backends import RosFileServerLoader

# Set high precision to import meshes defined in meters
compas.PRECISION = '12f'

# Load robot and its geometry
with RosClient('localhost') as ros:
    robot = ros.load_robot(load_geometry=True)
    print(robot.model)
