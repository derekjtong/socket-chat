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

connected_clients = set()


class ClientHandler:
    def __init__(self, link, client_address, client_uuid):
        self.link = link
        self.client_address = client_address
        self.client_uuid = client_uuid
        self.client_name = ""
        self.thread_name = f"[{threading.get_native_id()}]"
        self.target_id = -1

        self.command_handlers = {
            CMD_USERNAME: self.cmd_username,
            CMD_LIST: self.cmd_list,
            CMD_EXIT: self.cmd_exit,
            CMD_HISTORY: self.cmd_history,
            CMD_TARGET: self.cmd_target,
            CMD_HELP: self.cmd_help,
        }

    def send(self, message):
        self.link.sendall(message.encode())

    def run(self):
        print(
            f"[SERVER]: New connection from {self.client_address}, created new thread {self.thread_name}"
        )
        self.send(f"{self.thread_name} Server: Your UUID is {self.client_uuid}")
        while True:
            client_data = self.link.recv(1024).decode()
            if not client_data:
                print("empty")
                break
            if client_data[0] == "/":
                if self.handle_command(client_data) is False:
                    print(f"{self.thread_name}: Client {self.client_address} exited")
                    global connected_clients
                    connected_clients.remove(self.client_uuid)
                    break
            else:
                print(
                    f"{self.thread_name}: Client {self.client_address} sent message: {client_data}"
                )
                if self.target_id == -1:
                    self.send(
                        f"{self.thread_name} Server: No target selected. Select with /target <target_uuid>"
                    )
                else:
                    self.send(
                        f"{self.thread_name} Server: Sending message to {self.target_id}"
                    )
        self.link.close()

    def handle_command(self, command):
        print(
            f"{self.thread_name}: Client {self.client_address} used command {command}"
        )

        for cmd, handler in self.command_handlers.items():
            if command.startswith(cmd):
                return handler(command)

        # Default handler for unrecognized commands
        self.send(f"{self.thread_name} Server: Unrecognized command {command}")

    def cmd_username(self, command):
        self.client_name = self.get_args(command)
        self.send(f"{self.thread_name} Server: Hello {self.client_name}")

    def cmd_list(self, command):
        values = "\nActive Clients:\n"
        for value in connected_clients:
            values += str(value)
            if value == self.client_uuid:
                values += " (self)"
            values += "\n"
        self.send(values)

    def cmd_exit(self, command):
        return False

    def cmd_history(self, command):
        self.send(f"History with {self.target_id}")

    def cmd_target(self, command):
        global connected_clients
        self.target_id = uuid.UUID(self.get_args(command))
        if self.target_id == self.client_uuid:
            self.send(f"Error: cannot target self")
        elif self.target_id in connected_clients:
            self.send(f"Connected to {self.target_id}")
        else:
            self.send(f"Error: target not found. To see connected clients, try /list")

    def cmd_help(self, command):
        help_message = """
        Server Help:
        /help       - Display this help message.
        /username   - Set your username. Usage: /username <your_name>
        /list       - List all active client IDs.
        /history    - View your message history with current target.
        /target     - Set your message target. Usage: /target <target_uuid>
        /exit       - Exit the client.
        """
        self.send(f"{self.thread_name} Server: {help_message}")

    def get_args(self, command):
        _, arg = command.split(maxsplit=1)
        return arg


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <host> <port>")
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])

    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.bind((host, port))
    sk.listen()

    print(f"[SERVER]: Started listening on [{host}:{port}], awaiting clients...")

    while True:
        conn, address = sk.accept()
        client_uuid = uuid.uuid4()
        connected_clients.add(client_uuid)
        client_handler = ClientHandler(conn, address, client_uuid)
        t = threading.Thread(target=client_handler.run)
        t.start()


if __name__ == "__main__":
    main()
