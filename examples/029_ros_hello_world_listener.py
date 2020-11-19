import time

from roslibpy import Topic
from compas_fab.backends import RosClient

ROS_HOST, ROS_PORT = '9b701671837d.ngrok.io', 80

def receive_message(message):
    print('Heard talking: ' + message['data'])

#with RosClient('localhost') as client:
with RosClient(host=ROS_HOST, port=ROS_PORT) as client:
    print('[OK] Connected to ROS: \n')
    #listener = Topic(client, '/messages', 'std_msgs/String')
    listener = Topic(client, '/ur_joint_states', 'sensor_msgs/JointState')
    listener.subscribe(receive_message)

    while client.is_connected:
        time.sleep(1)
