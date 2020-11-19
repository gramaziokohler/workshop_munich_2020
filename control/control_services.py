import argparse
import functools
import io
import json
import math
import os
import time

import roslibpy
from compas_fab.backends import RosClient
from twisted.internet.task import LoopingCall

from ur_online_control.communication.client_wrapper import ClientWrapper
from ur_online_control.communication import msg_identifiers
from ur_online_control.communication.server import Server

# Locate file
HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

class PickAndPlaceTask(object):
    def __init__(self, ur):
        self.ur = ur

    def send_trajectory(self, name, points):
        print(' - Sending trajectory {}'.format(name))
        send_trajectory_points(points, self.ur)

    def set_gripper(self, value):
        print(' - Setting gripper {}'.format('ON' if value else 'OFF'))
        self.ur.send_command_airpick(value)
        self.ur.wait_for_ready()


def storage_handler(request, response):
    print('Received new assembly element task from user: {}'.format(request['username']))

    # Store request
    with io.open(os.path.join(DATA, '{}_{}.json'.format(request['username'], request['node_id'])), 'w') as f:
        json.dump(request, f, indent=2)

    response['success'] = True
    response['message'] = 'Yay!'
    return True


def execution_handler(request, response, ur=None):
    print('Task execution starting...\nElement key={}, User={}'.format(request['node_id'], request['username']))

    pick_trajectory = request['pick_trajectory']['points']
    move_trajectory = request['move_trajectory']['points']
    place_trajectory = request['place_trajectory']['points']

    task = PickAndPlaceTask(ur)
    task.send_trajectory('PICK', pick_trajectory)
    task.set_gripper(True)
    task.send_trajectory('REVERSED PICK', reversed(pick_trajectory))

    task.send_trajectory('MOVE', move_trajectory)

    task.send_trajectory('PLACE', place_trajectory)
    task.set_gripper(False)
    task.send_trajectory('REVERSED PLACE', reversed(place_trajectory))

    task.send_trajectory('MOVE BACK TO START', reversed(move_trajectory))

    print('Task execution completed!')

    response['success'] = True
    response['message'] = 'Executed!'
    return True

def send_trajectory_points(trajectory_points, ur):
    # TODO: Check if vel/accel make sense
    for point in trajectory_points:
        ur.send_command_movej([pd for pd in point['positions']], v=.1, a=.1)
    ur.wait_for_ready()

def joint_states_publisher(ur, topic):
    queue = ur.rcv_queues[msg_identifiers.MSG_CURRENT_POSE_JOINT]

    try:
        if queue.empty():
            return

        current_config = queue.get_nowait()
        if not current_config:
            return

        topic.publish(roslibpy.Message({
            'name':  ['shoulder_pan_joint', 'shoulder_lift_joint', 'elbow_joint', 'wrist_1_joint', 'wrist_2_joint', 'wrist_3_joint'],
            'position': [math.radians(j) for j in current_config],
            'velocity': [0.] * len(current_config),
            'effort': [0.] * len(current_config),
        }))
    except Exception as e:
        print('[EXCEPTION] Cannot publish joint state: {}'.format(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send assembly task service')
    parser.add_argument('-s', '--server-address', help='server address', default='127.0.0.1')
    parser.add_argument('-p', '--server-port', help='server port', default=30003)
    parser.add_argument('-u', '--ur-address', help='UR robot address', default='127.0.0.1')
    parser.add_argument('-f', '--frequency', help='Frequency to publish joint states (in HZ)', default=5)
    args = parser.parse_args()

    print('Starting UR control server...')
    print('Press CTRL+C to abort')
    print('NOTE: if CTRL+C does not abort cleanly, set the env variable to FOR_DISABLE_CONSOLE_CTRL_HANDLER=1')

    print('UR Server starting...', end='\r')
    server = Server(args.server_address, args.server_port)
    server.start()
    server.client_ips.update({'UR': args.ur_address})
    print('UR Server started.   ')

    print('Waiting for UR client...', end='\r')
    ur = ClientWrapper("UR")
    ur.wait_for_connected()
    print('UR client connected. Ready to process tasks.')

    print('ROS Nodes status:')
    print(' [ ] ROS Services', end='\r')
    client = RosClient('localhost', 80)
    #client = RosClient('192.168.10.12')
    storage_service = roslibpy.Service(client, '/store_assembly_task', 'workshop_tum_msgs/AssemblyTask')
    storage_service.advertise(storage_handler)

    execute_service = roslibpy.Service(client, '/execute_assembly_task', 'workshop_tum_msgs/AssemblyTask')
    execute_service.advertise(functools.partial(execution_handler, ur=ur))
    print(' [X] ROS Services')

    print(' [ ] ROS Topics', end='\r')
    joint_states_topic = roslibpy.Topic(client, '/ur_joint_states', 'sensor_msgs/JointState')
    joint_states_topic.advertise()

    joint_states_publisher_loop = LoopingCall(joint_states_publisher, **dict(ur=ur, topic=joint_states_topic))
    joint_states_publisher_loop.start(1 / args.frequency)
    print(' [X] ROS Topics')

    print('Ready!')

    client.run_forever()

    print('ROS Nodes status:')
    print(' [ ] ROS Services disconnection', end='\r')
    storage_service.unadvertise()
    execute_service.unadvertise()
    print(' [X] ROS Services disconnection')
    print(' [ ] ROS Topics disconnection', end='\r')
    joint_states_topic.unadvertise()
    print(' [X] ROS Topics disconnection')
    time.sleep(1)

    print('Disconnected')

    client.terminate()

    ur.quit()
    server.close()
