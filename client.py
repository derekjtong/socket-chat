import sys
import socket

# Check for the correct number of command-line arguments.
if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

# Extract the host and port from the command-line arguments.
host, port = sys.argv[1], int(sys.argv[2])

# Create a new socket for the client.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the client socket to the specified server's host and port.
client_socket.connect((host, port))

# Prompt the user for a username.
name = ""
while name == "":
    name = input("Username: ").strip()

client_socket.sendall(f"/username {name}".encode())
server_reply = client_socket.recv(1024).decode()
print(server_reply)
server_reply = client_socket.recv(1024).decode()
print(server_reply)

# Continuously prompt the user to enter messages to send to the server.
while True:
    message = input("SOCKETCHAT: ").strip()

    # If the user doesn't enter a message, skip to the next iteration.
    if not message:
        continue

    # Send the user's message to the server.
    client_socket.sendall(message.encode())

    # If the user enters "exit", log the exit message and break the loop.
    if message == "/exit":
        print("Exiting...")
        break

    # Receive and print the server's reply.
    print(client_socket.recv(1024).decode())

# Close the client socket after communication ends.
client_socket.close()
