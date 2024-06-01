"""
This script generates an Ansible Inventory file for a cluster on cloudlab.
"""
import argparse

def generate(args):
    import socket
    hostname = str(socket.gethostname())
    with open(args.gen_path, 'w+') as f:

        #-- Compute Nodes --
        f.write(f'computenodes:\n')
        f.write(f'  hosts:\n')
        for i in range(0, args.number_of_worker_nodes):
            node_name = hostname.replace('node0',f'node{i}')
            f.write(f'    {node_name}:\n')
        #-- Data Nodes --
        f.write(f'nfsnode:\n')
        f.write(f'  hosts:\n')
        nfs_node_name = hostname.replace('node0',f'data')
        f.write(f'    {nfs_node_name}:\n')
        #-- All variables --
        f.write(f'all:\n')
        f.write(f'  vars:\n')
        f.write(f'    ansible_user: root\n')
        f.write(f'    ansible_private_key_file: /root/.ssh/id_rsa\n')
        f.write(f'    ansible_host_key_checking: False\n')
        f.write(f'    numcomputenodes: {args.number_of_compute_nodes}\n')
        f.write(f'    nfshostname: {nfs_node_name}\n')
        if 'wisc.cloudlab.us' in hostname:
            f.write('    common_user_group: schedulingpower-\n')
        elif 'clemson.cloudlab.us' in hostname:
            f.write('    common_user_group: schedulingpower-\n')
        else:
            f.write('    common_user_group: SchedulingPower\n')
    pass


def parse_args():
    """
    Parse the args.
    """
    parser = argparse.ArgumentParser(description="Argument Parser")

    parser.add_argument("-n", "--number_of_compute_nodes", type=int, default=1,
                        help="Number of compute nodes(default: 1)")
    parser.add_argument("-C", "--gen_path", type=str, default="inventory.yml",
                        help="Path to traces (default: 'inventory.yml')")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    generate(args)