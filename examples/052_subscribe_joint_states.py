import argparse

import time

from roslibpy import Topic
from compas_fab.backends import RosClient

def receive_message(message):
    print(message)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Joint states publisher')
    parser.add_argument('-r', '--ros-host', help='ROS host', default='localhost')
    parser.add_argument('-p', '--ros-port', help='ROS port', default=9090)
    args = parser.parse_args()

    client = RosClient(host=args.ros_host, port=int(args.ros_port))

    # Subscribe to joint state updates
    listener = Topic(client, '/ur_joint_states', 'sensor_msgs/JointState')
    listener.subscribe(receive_message)

    # Start connection
    client.on_ready(lambda: print('[OK] Connected to ROS: \n'))
    client.run_forever()

    client.terminate()
