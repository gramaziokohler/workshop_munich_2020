import argparse
import functools
import io
import json
import math
import os

import roslibpy
from compas_fab.backends import RosClient
from twisted.internet.task import LoopingCall

from ur_online_control.communication.client_wrapper import ClientWrapper
from ur_online_control.communication import msg_identifiers
from ur_online_control.communication.server import Server

# Locate file
HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

def storage_handler(request, response):
    print('Received new assembly element task from user: {}'.format(request['username']))

    # Store request
    with io.open(os.path.join(DATA, '{}_{}.json'.format(request['username'], request['node_id'])), 'w') as f:
        json.dump(request, f, indent=2)

    response['success'] = True
    response['message'] = 'Yay!'
    return True

def execution_handler(request, response, ur=None):

    # start pickup
    print(' - Sending PICK trajectory')
    send_trajectory_points(request['pick_trajectory']['points'], ur)
    # set gripper ON
    print(' - Setting gripper ON')
    ur.send_command_airpick(True)
    ur.wait_for_ready()
    # send reversal
    print(' - Sending PICK trajectory reversed')
    send_trajectory_points(reversed(request['pick_trajectory']['points']), ur)

    # send kinematic trajectory
    print(' - Sending MOVE trajectory')
    send_trajectory_points(request['move_trajectory']['points'], ur)

    # start place
    print(' - Sending PLACE trajectory')
    send_trajectory_points(request['place_trajectory']['points'], ur)
    # set gripper OFF
    print(' - Setting gripper OFF')
    ur.send_command_airpick(False)
    ur.wait_for_ready()
    # send reversal
    print(' - Sending PLACE trajectory reversed')
    send_trajectory_points(reversed(request['place_trajectory']['points']), ur)

    # go back with a reversed kinematic trajectory
    print(' - Sending MOVE trajectory reversed')
    send_trajectory_points(reversed(request['move_trajectory']['points']), ur)

    response['success'] = True
    response['message'] = 'Executed!'
    return True

def send_trajectory_points(trajectory_points, ur):
    for point in trajectory_points:
        ur.send_command_movej([math.radians(pd) for pd in point['positions']], v=10., a=10.)
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
            'name': [],
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
    client = RosClient()
    storage_service = roslibpy.Service(client, '/store_assembly_task', 'workshop_tum_msgs/AssemblyTask')
    storage_service.advertise(storage_handler)

    execute_service = roslibpy.Service(client, '/execute_assembly_task', 'workshop_tum_msgs/AssemblyTask')
    execute_service.advertise(functools.partial(execution_handler, ur=ur))
    print(' [X] ROS Services')

    print(' [ ] ROS Topics', end='\r')
    joint_states_topic = roslibpy.Topic(client, '/joint_states', 'sensor_msgs/JointState')
    joint_states_topic.advertise()

    joint_states_publisher_loop = LoopingCall(joint_states_publisher, **dict(ur=ur, topic=joint_states_topic))
    joint_states_publisher_loop.start(1 / args.frequency)
    print(' [X] ROS Topics')

    print('Ready!')

    client.run_forever()
    client.terminate()

    ur.quit()
    server.close()
