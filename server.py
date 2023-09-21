import sys
import socket
import threading
import uuid

CMD_LIST = "/list"
CMD_EXIT = "/exit"
CMD_HISTORY = "/history"
CMD_USERNAME = "/username"
CMD_HELP = "/help"


def active_client_IDs():
    return "You".encode()


def handle_client(link, client, client_id):
    thread_name = f"[{threading.get_native_id()}]"
    client_name = ""

    print(
        "[SERVER]: New connection from [%s:%s], created new thread [%s]"
        % (client[0], client[1], thread_name)
    )
    print("%8s: Client [%s:%s] connected" % (thread_name, client[0], client[1]))

    link.sendall(f"{thread_name} Server: Your UUID is {client_id}".encode())

    while True:
        client_data = link.recv(1024).decode()
        if not client_data:
            print("empty")
            break
        if client_data[0] == "/":
            if (
                handle_command(link, client_data, thread_name, client, client_name)
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


def handle_command(link, command, thread_name, client, client_name):
    print(
        "%8s: Client [%s:%s] used command %s"
        % (thread_name, client[0], client[1], command)
    )
    if command.startswith(CMD_USERNAME):
        _, name = command.split(maxsplit=1)
        client_name = name
        link.sendall(f"{thread_name} Server: Hello {client_name}".encode())
    elif command == CMD_LIST:
        link.sendall(active_client_IDs())
    elif command == CMD_EXIT:
        return False
    elif command == CMD_HISTORY:
        pass
    elif command == CMD_USERNAME:
        pass
    elif command == CMD_HELP:
        help_message = """
        Server Help:
        /help       - Display this help message.
        /username   - Set your username. Usage: /username <YourName>
        /list       - List all active client IDs.
        /history    - View your message history (Note: This command is not yet implemented).
        /exit       - Exit the chat.
        """
        link.sendall(f"{thread_name} Server: {help_message}".encode())
    else:
        link.sendall(f"{thread_name} Server: Unrecognized command {command}".encode())


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
        # Start a new thread to handle the client connection.
        t = threading.Thread(target=handle_client, args=(conn, address, uuid.uuid4()))
        t.start()


if __name__ == "__main__":
    main()
