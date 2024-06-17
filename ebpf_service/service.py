import time
import logging
import socket
import threading


logging.basicConfig(
    level=logging.INFO,  # Adjust the logging level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/local/ebpf_service.log'),  # File handler
        logging.StreamHandler()  # Console handler
    ]
)

previous_value = None
do_something2_running = False
do_something2_thread = None

# Compile the eBPF program
def doSomething(value):
    # Your processing logic here (same as before)
    import time
    time.sleep(2)  # Simulate processing time
    return value

# Start eBPF listening
def doSomething2():
    global do_something2_running
    do_something2_running = True
    # print("doSomething2 started. Waiting for a matching value...")
    while do_something2_running:
        # Infinite loop (replace with your actual logic)
        pass  # Placeholder: Do nothing in the loop for now
    # print("doSomething2 terminated.")

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