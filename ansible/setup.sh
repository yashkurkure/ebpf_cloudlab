#!/bin/bash

num_nodes=$2
inventory_path=$3

# Install Ansible
sudo apt -y update
sudo apt -y install software-properties-common
sudo add-apt-repository --y --update ppa:ansible/ansible
sudo apt -y install ansible
sudo apt -y install python3-pip

# Generate Ansible Inventory
python3 /local/repository/ansible/inventory.py -n $num_nodes -C $inventory_path