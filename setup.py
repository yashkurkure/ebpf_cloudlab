import os
import ansible_runner
from rich.progress import Progress, BarColumn
from rich.logging import RichHandler
from rich.console import Console
import logging
import time

# --- Configuration ---
timestamp = time.strftime("%Y%m%d-%H%M%S")
log_dir = f"/local/ansible_logs/log_{timestamp}/"

# Ensure log directory exists
os.makedirs(log_dir, exist_ok=True)

# --- Logging Setup ---
# Create a custom formatter that adds timestamps to log messages
class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.msg = f"[{record.created:%Y-%m-%d %H:%M:%S}] {record.msg}"
        return super().format(record)

# Set up Rich logging and file logging
logging.basicConfig(level="INFO", format="%(message)s")
logger = logging.getLogger("ansible_runner")

# Configure rich handler for console output
console_handler = RichHandler(rich_tracebacks=True, console=Console(stderr=True))
console_handler.setFormatter(CustomFormatter())
logger.addHandler(console_handler)

# Configure file handler for log files
file_handler = logging.FileHandler(log_dir + "ansible.log")
file_handler.setFormatter(CustomFormatter())
logger.addHandler(file_handler)

# --- Ansible Runner Function ---
def run_playbook(playbook_name):
    with Progress(
        BarColumn(bar_width=None),  # Dynamic progress bar width
        "[progress.percentage]{task.percentage:>3.0f}%",
        transient=True,             # Hide the progress bar when complete
    ) as progress:
        task = progress.add_task(f"[green]Running '{playbook_name}'...", total=None)  # Initial unknown total

        def event_handler(event):
            if event["event"] == "playbook_on_task_start":
                progress.log(f"[bold blue]{event['task']}")  # Show task names
                progress.update(task, total=None)  # We don't know the total tasks yet

            progress.update(task, advance=1)  # Update progress on each event
            
            # Log all events to the log file
            logger.info(f"Event: {event}")

        runner = ansible_runner.run(
            private_data_dir='/local/repository/ansible',
            inventory='/local/cluster_inventory.yml',
            playbook=playbook_name,
            event_handler=event_handler,
            output_tee=True,  # Tee output to both log and console (for stdout/stderr)
        )

        if runner.status == "successful":
            progress.log(f"[bold green]Playbook '{playbook_name}' completed successfully")
        else:
            progress.log(f"[bold red]Playbook '{playbook_name}' failed")
            # Redirect all stdout/stderr from Ansible to the log file 
            logger.error(runner.stdout.strip() or runner.stderr.strip()) 

# --- Execute Playbooks ---
run_playbook('nfs.yml')
run_playbook('mpich.yml')