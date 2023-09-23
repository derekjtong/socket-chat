import sys
import socket
import threading
import uuid

# Client Commands
CMD_LIST = "/list"
CMD_EXIT = "/exit"
CMD_HISTORY = "/history"
CMD_USERNAME = "/username"
CMD_HELP = "/help"
CMD_TARGET = "/target"


def main():
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

        # Generate uuid
        client_uuid = uuid.uuid4()
        # Add connected clients to list
        connected_clients.append({"asfd", address, client_uuid})

        # Start a new thread to handle the client connection.
        t = threading.Thread(target=handle_client, args=(conn, address, client_uuid))
        t.start()


def active_client_IDs():
    global connected_clients

    for value in connected_clients:
        print(value)
        # link.sendall(value.client_uuid.encode())
    return


def get_args(command):
    _, arg = command.split(maxsplit=1)
    return arg


def get_history():
    pass


def handle_client(link, client, client_uuid):
    thread_name = f"[{threading.get_native_id()}]"
    client_name = ""

    print(
        "[SERVER]: New connection from [%s:%s], created new thread [%s]"
        % (client[0], client[1], thread_name)
    )
    print("%8s: Client [%s:%s] connected" % (thread_name, client[0], client[1]))

    link.sendall(f"{thread_name} Server: Your UUID is {client_uuid}".encode())

    while True:
        client_data = link.recv(1024).decode()
        if not client_data:
            print("empty")
            break
        if client_data[0] == "/":
            if (
                handle_command(
                    link, client_data, thread_name, client, client_name, client_uuid
                )
                is False
            ):
                print(
                    "%8s: Client [%s:%s] exited" % (thread_name, client[0], client[1])
                )
                break
        else:
            print(
                "%8s: Client [%s:%s] sent message: %s"
                % (thread_name, client[0], client[1], client_data)
            )
            link.sendall(f"{thread_name} Server: Received your message".encode())
    link.close()


def handle_command(link, command, thread_name, client, client_name, client_uuid):
    print(
        "%8s: Client [%s:%s] used command %s"
        % (thread_name, client[0], client[1], command)
    )
    if command.startswith(CMD_USERNAME):
        client_name = get_args(command)
        link.sendall(f"{thread_name} Server: Hello {client_name}".encode())

    elif command.startswith(CMD_LIST):
        active_client_IDs()
        link.sendall("LIST OF ACTIVE IDS".encode())

    elif command.startswith(CMD_EXIT):
        return False

    elif command.startswith(CMD_HISTORY):
        target_id = get_args(command)
        link.sendall(get_history(client_uuid, target_id))

    elif command.startswith(CMD_TARGET):
        target_id = get_args(command)
        
        link.sendall(f"Connected to {target_id}".encode())

    elif command == CMD_USERNAME:
        pass

    elif command.startswith(CMD_HELP):
        help_message = """
        Server Help:
        /help       - Display this help message.
        /username   - Set your username. Usage: /username <YourName>
        /list       - List all active client IDs.
        /history    - View your message history with current target/
        /target     - Set your message target. Usage: /target <target_uuid>
        /exit       - Exit the client.
        """
        link.sendall(f"{thread_name} Server: {help_message}".encode())

    else:
        link.sendall(f"{thread_name} Server: Unrecognized command {command}".encode())


connected_clients = []


if __name__ == "__main__":
    main()
