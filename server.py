import sys
import socket
import threading
import uuid


def link_handler(link, client, id):
    """
    Handle individual client connections in separate threads.

    :param link: The socket connection to the client.
    :param client: A tuple containing the client's IP and port.
    :param id: A unique UUID assigned to the client.
    """
    # Get the native thread ID for logging purposes.
    thread_id = threading.get_native_id()

    # Log the new connection and the thread handling it.
    print(
        "[SERVER]: New connection from [%s:%s], created new thread [%s]"
        % (address[0], address[1], thread_id)
    )
    print(" [%s]: Client [%s:%s] connected" % (thread_id, client[0], client[1]))

    # Continuously listen for messages from the client.
    while True:
        client_data = link.recv(1024).decode()
        if client_data == "exit":
            # If the client sends "exit", log the disconnection and break the loop.
            print(
                " [%s]: Client [%s:%s] ended communication"
                % (thread_id, client[0], client[1])
            )
            break
        # Log the received message from the client.
        print(
            " [%s]: Client [%s:%s] sent message: %s"
            % (thread_id, client[0], client[1], client_data)
        )
        try:
            # Send a response back to the client with its UUID.
            link.sendall(f"[{thread_id}] Server: Your UUID is {id}".encode())
        except BrokenPipeError:
            # Handle the case where the client forcibly closes the connection.
            print(
                " [%s]: Client [%s:%s] forcibly closed the connection."
                % (thread_id, client[0], client[1])
            )
            break
    # Close the connection to the client.
    link.close()


# Check for the correct number of command-line arguments.
if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

# Extract the host and port from the command-line arguments.
host, port = sys.argv[1], int(sys.argv[2])

# Create a new socket and bind it to the specified host and port.
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.bind((host, port))
sk.listen()

# Log that the server has started and is listening for connections.
print("[SERVER]: Started listening on [%s:%s], awaiting clients..." % (host, port))

# Continuously listen for incoming client connections.
while True:
    conn, address = sk.accept()
    # Start a new thread to handle the client connection.
    t = threading.Thread(target=link_handler, args=(conn, address, uuid.uuid4()))
    t.start()
