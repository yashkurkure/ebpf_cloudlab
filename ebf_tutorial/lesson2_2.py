from bcc import BPF
from bcc.utils import printb

def replace_syscall(original_string, replacement_text):
    new_string = original_string[:]
    new_string = new_string.replace("SYSCALL", replacement_text)
    return new_string

header = '''
#include <linux/sched.h>

// define output data structure in C
struct data_t {
    u32 category;
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
    char syscall_name[100];
};
BPF_PERF_OUTPUT(events);
'''

probe_code = '''
int syscall_probe_SYSCALL(void *ctx) {
    struct data_t data = {};

    data.syscall_name = "SYSCALL\0"
    data.category = 0;
    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}

int syscall_retprobe_SYSCALL(void *ctx) {
    struct data_t data = {};

    data.syscall_name = "SYSCALL\0"
    data.category = 1;
    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}
'''

# execve
execve_code = replace_syscall(probe_code, 'execve')

# fork
fork_code = replace_syscall(probe_code, 'fork')

# exit
exit_code = replace_syscall(probe_code, 'exit')

# merge all code
program = header + '\n' + execve_code + '\n' + fork_code + '\n' + exit_code

b = BPF(text=program)
execve_fnname = b.get_syscall_fnname("execve")
b.attach_kprobe(event=execve_fnname, fn_name="syscall_probe_execve")
b.attach_kretprobe(event=execve_fnname, fn_name="syscall_retprobe_execve")

fork_fnname = b.get_syscall_fnname("fork")
b.attach_kprobe(event=execve_fnname, fn_name="syscall_probe_fork")
b.attach_kretprobe(event=execve_fnname, fn_name="syscall_retprobe_fork")

fork_fnname = b.get_syscall_fnname("exit")
b.attach_kprobe(event=execve_fnname, fn_name="syscall_probe_exit")
b.attach_kretprobe(event=execve_fnname, fn_name="syscall_retprobe_exit")

# header
print('Tracing syscalls... Ctrl-C to end.')
print("%-18s %-16s %-6s %s %s" % ("TIME(s)", "COMM", "PID", "CATEGORY", "SYSCALL NAME"))

# process event
start = 0


def print_event(cpu, data, size):
    global start
    event = b["events"].event(data)
    time_s = (float(event.ts)) / 1000000000
    printb(
        b"%-18.9f %-16s %-6d %d %s"
        % (time_s, event.comm, event.pid, event.category, event.syscall_name)
    )

# loop with callback to print_event
b["events"].open_perf_buffer(print_event)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
