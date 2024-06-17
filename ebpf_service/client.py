import socket
import sys

def main():
    if len(sys.argv) < 2:  # Check if at least one argument is provided
        print("Usage: python client.py <integer_value>")
        return

    try:
        value = int(sys.argv[1])  # Get the integer from command line
    except ValueError:
        print("Invalid input. Please provide an integer.")
        return

    server_address = ('localhost', 8080)  # (host, port) 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    client_socket.send(str(value).encode())  # Send the integer
    response = client_socket.recv(1024)  # Receive the response
    print(f"Server response: {response.decode()}") 

    client_socket.close()

if __name__ == "__main__":
    main()