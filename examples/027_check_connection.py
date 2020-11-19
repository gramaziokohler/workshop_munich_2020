from compas_fab.backends import RosClient

#with RosClient('localhost') as client:
with RosClient('af41953ec075.ngrok.io', 80) as client:

    print('Connected:', client.is_connected)
