import ansible_runner
from rich.progress import Progress
from rich.logging import RichHandler
import logging
import time

# Create a timestamp for the log directory
timestamp = time.strftime("%Y%m%d-%H%M%S")
log_dir = f"/local/ansible_logs/log_{timestamp}/"

# Set up logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True), logging.FileHandler(log_dir + "ansible.log")],
)

def run_playbook(playbook_name):
    with Progress() as progress:
        task = progress.add_task(f"[green]Running '{playbook_name}'...", total=None)  # Total unknown initially

        runner = ansible_runner.run(
            private_data_dir='/local/repository/ansible',
            inventory='/local/cluster_inventory.yml',
            playbook=playbook_name,
            event_handler=lambda event: progress.update(task, advance=1),  # Update progress on each event
        )

        if runner.status == "successful":
            progress.log(f"[bold green]Playbook '{playbook_name}' completed successfully")
        else:
            progress.log(f"[bold red]Playbook '{playbook_name}' failed")
            progress.log(runner.stdout)

# Run the playbooks
run_playbook('nfs.yml')
run_playbook('mpich.yml')