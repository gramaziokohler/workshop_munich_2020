import argparse
import functools
import io
import json
import os
import time

import roslibpy
from compas_fab.backends import RosClient

# Locate file
HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))


def joint_states_publisher(topic, frequency):
    print('Starting joint states publisher...')

    while topic.ros.is_connected:
        time.sleep(1. / frequency)

        try:
            with io.open(os.path.join(DATA, 'current-config.json'), 'r') as cc:
                config_msg = json.load(cc)

            topic.publish(roslibpy.Message(config_msg))
        except Exception as e:
            print('[EXCEPTION] Cannot publish joint state: {}'.format(e))

    print('Joint state publisher disconnected')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Joint states publisher')
    parser.add_argument('-f', '--frequency', help='Frequency to publish joint states (in HZ)', default=5)
    args = parser.parse_args()

    print('Starting UR joint state publisher...')
    print('Press CTRL+C to abort')
    print('NOTE: if CTRL+C does not abort cleanly, set the env variable to FOR_DISABLE_CONSOLE_CTRL_HANDLER=1')

    print('ROS Nodes status:')
    client = RosClient('localhost', 80)
    #client = RosClient('192.168.10.12')

    print(' [ ] ROS Topics', end='\r')
    joint_states_topic = roslibpy.Topic(client, '/ur_joint_states', 'sensor_msgs/JointState')
    joint_states_topic.advertise()

    client.on_ready(functools.partial(joint_states_publisher, topic=joint_states_topic, frequency=args.frequency))
    print(' [X] ROS Topics')

    print('Ready!')

    client.run_forever()

    print('ROS Nodes status:')
    print(' [ ] ROS Topics disconnection', end='\r')
    joint_states_topic.unadvertise()
    print(' [X] ROS Topics disconnection')
    time.sleep(1)

    print('Disconnected')

    client.terminate()
