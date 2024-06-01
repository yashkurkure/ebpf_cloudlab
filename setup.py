import ansible_runner

runner = ansible_runner.run(
    private_data_dir='/local/repository/ansible',
    inventory='/local/cluster_inventory.yml',
    playbook='nfs.yml',
)

if runner.status == "successful":
    print("Playbook completed successfully")
else:
    print("Playbook failed")
    print(runner.stdout)