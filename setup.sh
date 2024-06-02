ansible-playbook \
    -i /local/cluster_inventory.yml\
    /local/repository/ansible/ebpf.yml

ansible-playbook \
    -i /local/cluster_inventory.yml\
    /local/repository/ansible/nfs.yml

ansible-playbook \
    -i /local/cluster_inventory.yml\
    /local/repository/ansible/mpich.yml

ansible-playbook \
    -i /local/cluster_inventory.yml\
    --extra-vars "username=ykurkure"\
    /local/repository/ansible/ssh.yml