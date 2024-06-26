import socket
import threading

previous_value = None
do_something2_running = False
do_something2_thread = None

def doSomething(value):
    # Your processing logic here (same as before)
    import time
    time.sleep(2)  # Simulate processing time
    return value * 2

def doSomething2():
    global do_something2_running
    do_something2_running = True
    print("doSomething2 started. Waiting for a matching value...")
    while do_something2_running:
        # Infinite loop (replace with your actual logic)
        pass  # Placeholder: Do nothing in the loop for now
    print("doSomething2 terminated.")

def handle_client(client_socket):
    global previous_value, do_something2_running, do_something2_thread

    data = client_socket.recv(1024)
    try:
        value = int(data.decode())
        result = doSomething(value)
        client_socket.send(str(result).encode())

        if previous_value is None:
            previous_value = value
            do_something2_thread = threading.Thread(target=doSomething2)
            do_something2_thread.start()
        elif value == previous_value:
            do_something2_running = False
            do_something2_thread.join()  # Wait for the thread to finish

    except ValueError:
        client_socket.send("Invalid input. Please send an integer.".encode())
    finally:
        client_socket.close()

def main():
    server_address = ('localhost', 8080) 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(server_address)
    server_socket.listen(1)  # Allow only one connection

    print("Server is listening for a client...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")

        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    main()
