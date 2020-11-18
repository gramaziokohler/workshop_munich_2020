import io
import os
import json
import roslibpy
from compas_fab.backends import RosClient

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
    client = RosClient()
    service = roslibpy.Service(client, '/send_assembly_task', 'workshop_tum_msgs/SendAssemblyTask')
    service.advertise(handler)
    print('Service advertised, waiting for clients...')
    print('Press CTRL+C to abort')
    print('NOTE: if CTRL+C does not abort cleanly, set the env variable to FOR_DISABLE_CONSOLE_CTRL_HANDLER=1')

    client.run_forever()
    client.terminate()
