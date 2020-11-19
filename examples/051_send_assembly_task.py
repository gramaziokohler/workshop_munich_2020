import os

import roslibpy
from assembly_information_model.assembly import Assembly
from compas_fab.backends import RosClient


def get_planned_element_keys(assembly):
    return sorted(list(assembly.network.nodes_where({'is_planned': True })))

def send_element_trajectories(client, assembly, element_key):
    element = assembly.element(element_key)

    if len(element.trajectory) != 3:
        raise Exception('Element {} does not have all 3 trajectories planned'.format(element_key))

    pick_trajectory, move_trajectory, place_trajectory = element.trajectory

    print('[  ] Invoking ROS service...', end='\r')
    service = roslibpy.Service(client, '/store_assembly_task', 'workshop_tum_msgs/AssemblyTask')
    request = roslibpy.ServiceRequest(dict(
        node_id=str(element_key),
        username=username,
        pick_trajectory=client._convert_to_ros_trajectory(pick_trajectory).msg,
        move_trajectory=client._convert_to_ros_trajectory(move_trajectory).msg,
        place_trajectory=client._convert_to_ros_trajectory(place_trajectory).msg
    ))

    response = service.call(request)
    print('[{}] Received service response: {}'.format('OK' if response['success'] else '!!', response['message']))


def input_non_empty_string(message, default=None):
    while True:
        print(message, end='')
        input_string = input()
        if len(input_string) > 0:
            return input_string
        if default:
            return default

def input_non_zero_number(message):
    while True:
        print(message, end='')
        input_number = input()
        try:
            input_number = int(input_number)
            if input_number > -1:
                return input_number
        except ValueError:
            continue

if __name__ == '__main__':
    # Settings
    ROS_HOST, ROS_PORT = 'localhost', 9090

    # Locate file
    HERE = os.path.dirname(__file__)
    DATA = os.path.abspath(os.path.join(HERE, "..", "data"))
    DEFAULT_FILENAME = '047_plan_paths_assembly.json'

    print(r'__  __  __  __ ___   __ __     ___ __  __      ')
    print(r'|__)/  \|__)/  \ |   /  /  \|\ | | |__)/  \|   ')
    print(r'| \ \__/|__)\__/ |   \__\__/| \| | | \ \__/|__ ')
    print()

    username = input_non_empty_string('Please enter your name: ')

    filename = input_non_empty_string('Please enter the assembly file name [{}]: '.format(DEFAULT_FILENAME), DEFAULT_FILENAME)
    filepath = os.path.join(DATA, filename)
    if not os.path.isfile(filepath):
        raise FileNotFoundError('Could not file assembly json file: ' + filepath)

    # Load assembly
    print('\n[  ] Loading assembly...', end='\r')
    assembly = Assembly.from_json(filepath)
    print('[OK] Assembly loaded: {} '.format(filename))

    planned_elemement_keys = get_planned_element_keys(assembly)
    print('[OK] Found {} planned elements out of {} total elements'.format(len(planned_elemement_keys), assembly.number_of_elements()))
    print('[OK] Planned sequence: {}'.format(planned_elemement_keys))

    # Connect client
    print('[  ] Connecting to ROS {}:{}'.format(ROS_HOST, ROS_PORT), end='\r')
    with RosClient(host=ROS_HOST, port=ROS_PORT) as client:
        print('[OK] Connected to ROS: \n')

        # Start UI loop to send elements
        while True:
            element_key = input_non_zero_number('Please enter the element key to send for execution: ')
            if element_key not in planned_elemement_keys:
                print(' » Element not found, must be one of the planned element keys')
                continue

            send_element_trajectories(client, assembly, element_key)
