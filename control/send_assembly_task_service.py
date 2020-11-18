import io
import os
import json
import roslibpy
from compas_fab.backends import RosClient
import argparse

from ur_online_control.communication.server import Server
from ur_online_control.communication.client_wrapper import ClientWrapper
from ur_online_control.communication.formatting import format_commands
from ur_online_control.communication.msg_identifiers import *

# Locate file
HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, "..", "data"))

def handler(request, response):
    print('Received new assembly element task from user: {}'.format(request['username']))

    # Store request
    with io.open(os.path.join(DATA, '{}_{}.json'.format(request['username'], request['node_id'])), 'w') as f:
        json.dump(request, f, indent=2)

    response['success'] = True
    response['message'] = 'Yay!'
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send assembly task service')
    parser.add_argument('-s', '--server-address', help='server address', default='127.0.0.1')
    parser.add_argument('-p', '--server-port', help='server port', default=30003)
    parser.add_argument('-u', '--ur-address', help='UR robot address', default='127.0.0.1')
    args = parser.parse_args()

    print('Starting UR control server...')
    print('Press CTRL+C to abort')
    print('NOTE: if CTRL+C does not abort cleanly, set the env variable to FOR_DISABLE_CONSOLE_CTRL_HANDLER=1')

    print('ROS Service starting...', end='\r')
    client = RosClient()
    service = roslibpy.Service(client, '/send_assembly_task', 'workshop_tum_msgs/SendAssemblyTask')
    service.advertise(handler)
    print('Service advertised.    ')

    print('UR Server starting...', end='\r')
    server = Server(args.server_address, args.server_port)
    server.start()
    server.client_ips.update({'UR': args.ur_address})
    print('UR Server started.   ')

    print('Waiting for UR client...', end='\r')
    ur = ClientWrapper("UR")
    ur.wait_for_connected()
    print('UR client connected. Ready to process tasks.')


    client.run_forever()
    client.terminate()

    ur.quit()
    server.close()
