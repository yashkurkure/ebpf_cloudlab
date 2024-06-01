# type: ignore - Ignore Pylance
"""
Sets up a MPI cluster with eBPF

Instructions:
Wait for the experiment to start. SSH into node0 and run /local/setup.sh.
"""
# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as rspec
# Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal context, needed to defined parameters
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Number of nodes, minimum 1.
pc.defineParameter("nodeCount", "Number of  Nodes", portal.ParameterType.INTEGER, 1,
                   longDescription="Specify atleast 1 worker node")


# Pick your OS.
imageList = [
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04')
    ]

pc.defineParameter("osImage", "Select OS image",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList,
                   longDescription="Using Ubuntu 20.04")



# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()
# Check parameter validity.
if params.nodeCount < 1:
    pc.reportError(portal.ParameterError("You must choose at least 1 node.", ["nodeCount"]))
nodeCount = params.nodeCount

# Create link/lan.
lan = request.LAN()
# Process nodes, adding to lan.
nodes = []
for i in range(nodeCount):

    name = "node" + str(i)
    node = request.RawPC(name)
    node.installRootKeys(True, True)
    # Setup Ansible
    sa_command = "/local/repository/ansible/setup.sh "\
        + str(loginNodeCount)\
        + " "\
        + str(workerNodeCount)\
        + " /local/cluster_inventory.yml"
    node.addService(rspec.Execute(shell="bash", command=sa_command))

    # OS
    if params.osImage and params.osImage != "default":
        node.disk_image = params.osImage
    
    # Add to lan
    iface = node.addInterface("eth1")
    lan.addInterface(iface)
    

# Allocate data node
node = request.RawPC("data")
node.disk_image = params.osImage
bs = node.Blockstore("bs", "/exports/shared")
bs.size = "250GB"
iface = node.addInterface("eth1")
lan.addInterface(iface)
node.installRootKeys(True, True)

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)