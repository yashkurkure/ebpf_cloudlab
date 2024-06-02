#!/bin/bash

num_nodes=$1
inventory_path=$2

# Install Ansible
sudo apt -y update
sudo apt -y install software-properties-common
sudo add-apt-repository --y --update ppa:ansible/ansible
sudo apt -y install ansible
pip3 install ansible-runner

# Generate Ansible Inventory
python3 /local/repository/ansible/inventory.py -n $num_nodes -C $inventory_path