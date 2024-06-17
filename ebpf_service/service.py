from time import sleep, strftime
import logging
import socket
import threading
from bcc import BPF
from bcc.utils import printb
from bcc.syscall import syscall_name, syscalls


logging.basicConfig(
    level=logging.INFO,  # Adjust the logging level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/local/ebpf_service.log'),  # File handler
        logging.StreamHandler()  # Console handler
    ]
)

bpf = None
previous_value = None
do_something2_running = False
do_something2_thread = None
text = """
#include <linux/sched.h>

#ifdef LATENCY
struct data_t {
    u64 count;
    u64 total_ns;
};

BPF_HASH(start, u64, u64);
BPF_HASH(data, u32, struct data_t);
#else
BPF_HASH(data, u32, u64);
#endif

#ifdef LATENCY
TRACEPOINT_PROBE(raw_syscalls, sys_enter) {
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;
    u32 tid = (u32)pid_tgid;

#ifdef FILTER_SYSCALL_NR
    if (args->id != FILTER_SYSCALL_NR)
        return 0;
#endif

#ifdef FILTER_PID
    if (pid != FILTER_PID)
        return 0;
#endif

#ifdef FILTER_TID
    if (tid != FILTER_TID)
        return 0;
#endif

#ifdef FILTER_PPID
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    u32 ppid = task->real_parent->tgid;
    if (ppid != FILTER_PPID)
        return 0;
#endif

    u64 t = bpf_ktime_get_ns();
    start.update(&pid_tgid, &t);
    return 0;
}
#endif

TRACEPOINT_PROBE(raw_syscalls, sys_exit) {
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;
    u32 tid = (u32)pid_tgid;

#ifdef FILTER_SYSCALL_NR
    if (args->id != FILTER_SYSCALL_NR)
        return 0;
#endif

#ifdef FILTER_PID
    if (pid != FILTER_PID)
        return 0;
#endif

#ifdef FILTER_TID
    if (tid != FILTER_TID)
        return 0;
#endif

#ifdef FILTER_PPID
    struct task_struct *task = (struct task_struct *)bpf_get_current_task();
    u32 ppid = task->real_parent->tgid;
    if (ppid != FILTER_PPID)
        return 0;
#endif

#ifdef FILTER_FAILED
    if (args->ret >= 0)
        return 0;
#endif

#ifdef FILTER_ERRNO
    if (args->ret != -FILTER_ERRNO)
        return 0;
#endif

#ifdef BY_PROCESS
    u32 key = pid_tgid >> 32;
#else
    u32 key = args->id;
#endif

#ifdef LATENCY
    struct data_t *val, zero = {};
    u64 *start_ns = start.lookup(&pid_tgid);
    if (!start_ns)
        return 0;

    val = data.lookup_or_try_init(&key, &zero);
    if (val) {
        lock_xadd(&val->count, 1);
        lock_xadd(&val->total_ns, bpf_ktime_get_ns() - *start_ns);
    }
#else
    u64 *val, zero = 0;
    val = data.lookup_or_try_init(&key, &zero);
    if (val) {
        lock_xadd(val, 1);
    }
#endif
    return 0;
}
"""
def get_time_stamp():
    """
    Returns the current time as a string.
    Time format: %m-%d-%Y-%H-%M-%S
    """
    from datetime import datetime
    now = datetime.now()
    date_time = now.strftime("%m-%d-%Y-%H-%M-%S")
    return date_time

# Compile the eBPF program
def doSomething(value):
    global bpf
    # Your processing logic here (same as before)
    text = ("#define FILTER_PPID %d\n" % value) + text
    bpf = BPF(text=text)
    return value

# Print syscount results
def doSomething2():
    global do_something2_running
    do_something2_running = True
    htab_batch_ops = True if BPF.kernel_struct_has_field(b'bpf_map_ops',
        b'map_lookup_and_delete_batch') == 1 else False
    
    while True:
        sleep(1)
        timestamp = get_time_stamp()
        result_file_path = f'/local/counts-{timestamp}.log'
        data = bpf["data"]
        for k, v in sorted(data.items_lookup_and_delete_batch()
                        if htab_batch_ops else data.items(),
                        key=lambda kv: -kv[1].value)[:300]:
            if k.value == 0xFFFFFFFF:
                continue    # happens occasionally, we don't need it
            with open(result_file_path, "w") as f:
                # Write to the file here
                f.write(f'{syscall_name(k.value)} {v.value}\n')
        print("")
        if not htab_batch_ops:
            data.clear()

def handle_client(client_socket):
    global previous_value, do_something2_running, do_something2_thread

    # Get the sent PID
    data = client_socket.recv(1024)
    
    try:
        value = int(data.decode())
        logging.info(f"Received PID {value}")

        # No previous PID
        if previous_value is None:
            logging.info(f"TODO..start compiling ebpf code...")
            result = doSomething(value)
            logging.info(f"TODO..done compiling ebpf code...")
            client_socket.send(str(result).encode())
            previous_value = value
            logging.info(f"TODO..run ebpf code...")
            do_something2_thread = threading.Thread(target=doSomething2)
            do_something2_thread.start()
        
        # Previous PID
        elif value == previous_value:
            do_something2_running = False
            do_something2_thread.join()  # Wait for the thread to finish
            result = doSomething(value)
            client_socket.send(str(result).encode())
            logging.info(f"TODO..stopping ebpf code...")

    except ValueError:
        client_socket.send("Invalid input. Please send an integer.".encode())
    finally:
        client_socket.close()

def start_server():
    server_address = ('localhost', 8080) 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(server_address)
    server_socket.listen(1)  # Allow only one connection

    logging.info("Server started successfully.")
    while True:
        client_socket, addr = server_socket.accept()
        logging.info(f"Accepted connection from {addr}")

        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()


if __name__ == '__main__':
    logging.info("Service started.")
    start_server()