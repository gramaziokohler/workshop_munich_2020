# Before running this example, you have to:
# 1) install the example library in your environment:
#    pip install -e rpc_example
# 2) (optional) start the RPC server from Anaconda Prompt
#    compas_rpc start
#
# After that, you can run this file in VS Code or in Rhino/GH
#
from compas.rpc import Proxy

proxy = Proxy('rpc_functions', python='python')
print(proxy.mean_of_random_array())
