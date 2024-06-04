from bcc import BPF
from bcc.utils import printb

program = '''
#include <linux/sched.h>

// define output data structure in C
struct data_t {
    u32 category;
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
};
BPF_PERF_OUTPUT(events);

int kprobe__execve(void *ctx) {
    struct data_t data = {};

    data.category = 0;
    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}

int kretprobe__execve(void *ctx) {
    struct data_t data = {};

    data.category = 1;
    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}
'''
print('Tracing execve()... Ctrl-C to end.')

b = BPF(text=program)

# header
print("%-18s %-16s %-6s %s" % ("TIME(s)", "COMM", "PID", "CATEGORY"))

# process event
start = 0


def print_event(cpu, data, size):
    global start
    event = b["events"].event(data)
    time_s = (float(event.ts)) / 1000000000
    printb(
        b"%-18.9f %-16s %-6d %d"
        % (time_s, event.comm, event.pid, event.category)
    )

# loop with callback to print_event
b["events"].open_perf_buffer(print_event)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
