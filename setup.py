from ansible_runner import run
import os

inventory_path = "/local/cluster_inventory.yml"

playbooks = [
    # ("/local/repository/ansible/nfs.yml", None),
    # ("/local/repository/ansible/mpich.yml", None),
    # ("/local/repository/ansible/ssh.yml", {"username": "ykurkure"}),
    ("/local/repository/ansible/ebpf.yml", None),
]

for playbook_path, extravars in playbooks:
    result = run(
        playbook=playbook_path,
        inventory=inventory_path,
        extravars=extravars,
    )

    if result.status == "successful":
        print(f"Playbook '{playbook_path}' executed successfully:")
    else:
        print(f"Error executing playbook '{playbook_path}':")
        print(result.stderr)