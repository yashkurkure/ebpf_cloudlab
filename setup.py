from ansible_runner import run
import shutil
import os

inventory_path = "/local/cluster_inventory.yml"

playbooks = [
    ("/local/repository/ansible/mpich.yml", None),
    ("/local/repository/ansible/ssh.yml", {"username": "ykurkure"}),
    ("/local/repository/ansible/nfs.yml", None),
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

source_path = "/local/repository/mpi_job"
destination_path = "/shared/mpi_job"  # Include "mpi_job" in the path

# Create destination directory if it doesn't exist
os.makedirs(os.path.dirname(destination_path), exist_ok=True)

shutil.copytree(source_path, destination_path)
print(f"Directory '{source_path}' copied to '{destination_path}' successfully.")