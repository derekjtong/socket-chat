import sys
import socket
import threading
import uuid
import config

MESSAGE_BUFFER_SIZE = config.MESSAGE_BUFFER_SIZE
SOCKET_SETUP = config.SOCKET_SETUP
DEFAULT_CONNECTION = config.DEFAULT_CONNECTION

# Client Commands
CMD_LIST = "/list"
CMD_EXIT = "/exit"
CMD_HISTORY = "/history"
CMD_USERNAME = "/username"
CMD_HELP = "/help"
CMD_TARGET = "/target"


class ServerState:
    def __init__(self):
        self._connected_clients = {}
        self._connected_clients_lock = threading.Lock()
        self._connected_client_name = {}
        self._connected_client_name_lock = threading.Lock()

    def add_client(self, client_uuid, conn_send):
        with self._connected_clients_lock:
            self._connected_clients[client_uuid] = conn_send

    def remove_client(self, client_uuid):
        with self._connected_clients_lock:
            del self._connected_clients[client_uuid]

    def get_client(self, client_uuid):
        with self._connected_clients_lock:
            return self._connected_clients.get(client_uuid)

    def set_client_name(self, client_uuid, client_name):
        with self._connected_client_name_lock:
            self._connected_client_name[client_uuid] = client_name

    def get_client_name(self, client_uuid):
        with self._connected_client_name_lock:
            return self._connected_client_name.get(client_uuid)

    def get_all_clients(self):
        with self._connected_clients_lock, self._connected_client_name_lock:
            # Creating a list of tuples, each containing the UUID and name of a client
            return [
                (uuid, self._connected_client_name.get(uuid))
                for uuid in self._connected_clients
            ]


class ClientHandler:
    def __init__(
        self, conn_recv, addr_recv, conn_send, addr_send, client_uuid, server_state
    ):
        self.conn_recv = conn_recv  # client to server
        self.addr_recv = addr_recv

        self.conn_send = conn_send  # server to client
        self.addr_send = addr_send

        self.client_uuid = client_uuid
        self.server_state = server_state

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
        self.conn_send.sendall(f"[SERVER] {message}".encode())

    def run(self):
        print(f"{self.thread_name} Accepting connection from {self.addr_recv}")
        self.send(f"Your UUID is {self.client_uuid}")
        while True:
            client_data = self.conn_recv.recv(MESSAGE_BUFFER_SIZE).decode()
            if not client_data:
                print(
                    f"{self.thread_name} Client {self.addr_recv} disconnected unexpectedly"
                )
                self.server_state.remove_client(self.client_uuid)
                break
            if client_data[0] == "/":
                if self.handle_command(client_data) is False:
                    # Exited
                    break
            else:
                print(
                    f"{self.thread_name} Client {self.addr_recv} sent message: {client_data}"
                )
                if self.target_id == -1:
                    self.send(f"No target selected. Select with /target <target_uuid>")
                else:
                    self.send(f"Sending message to {self.target_id}")
                    self.send_to_target(client_data)
        self.conn_recv.close()
        self.conn_send.close()

    def handle_command(self, command):
        print(f"{self.thread_name} Client {self.addr_recv} used command {command}")

        for cmd, handler in self.command_handlers.items():
            if command.startswith(cmd):
                return handler(command)

        # Default handler for unrecognized commands
        self.send(f"Unrecognized command {command}")

    def cmd_username(self, command):
        self.client_name = self.get_args(command)
        self.send(f"Hello {self.client_name}")
        self.server_state.set_client_name(self.client_uuid, self.client_name)

    def cmd_list(self, command):
        values = "Active Clients:\n"
        for uuid, name in self.server_state.get_all_clients():
            values += f"    {uuid} {name}"
            if uuid == self.client_uuid:
                values += " (self)"
            values += "\n"
        self.send(values)

    def cmd_exit(self, command):
        print(f"{self.thread_name} Client {self.addr_recv} exited")
        self.server_state.remove_client(self.client_uuid)
        return False

    def cmd_history(self, command):
        self.send(f"History with {self.target_id}")
        # TODO

    def cmd_target(self, command):
        args = self.get_args(command)
        if not args:
            if self.target_id == -1:
                self.send(f"No target selected. Select with /target <target_uuid>")
            else:
                self.send(f"Current target: {self.target_id}")
            return

        try:
            temp_target_id = uuid.UUID(args)
        except ValueError:
            self.send(f"Error: target not found. To see connected clients, try /list")
            return

        if self.target_id == self.client_uuid:
            self.send(f"Error: cannot target self")
            return
        if self.server_state.get_client(temp_target_id):
            self.target_id = temp_target_id
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
        self.send(f"{help_message}")

    def get_args(self, command):
        parts = command.split(maxsplit=1)
        if len(parts) == 2:
            return parts[1]
        else:
            return False

    def send_to_target(self, client_data):
        try:
            target_connection = self.server_state.get_client(self.target_id)
            target_connection.sendall(f"\n{self.client_uuid}: {client_data}".encode())
        except Exception as e:
            print(f"Error handling client {self.target_id}: {e}")


def main():
    if len(sys.argv) != 3:
        # print(f"Usage: {sys.argv[0]} <host> <port>")
        # sys.exit(1)
        host, port = DEFAULT_CONNECTION
    else:
        host, port = sys.argv[1], int(sys.argv[2])

    socket_in = socket.socket(*SOCKET_SETUP)
    socket_in.bind((host, port))
    socket_in.listen()

    print(f"[SERVER] Started listening on [{host}:{port}], awaiting clients...")

    server_state = ServerState()
    while True:
        conn_recv, addr_recv = socket_in.accept()
        client_uuid = uuid.uuid4()

        # Set up server->client socket
        socket_out = socket.socket(*SOCKET_SETUP)
        socket_out.bind((host, 0))
        socket_out.listen()
        conn_recv.sendall(str(socket_out.getsockname()[1]).encode())
        conn_send, addr_send = socket_out.accept()

        # Add to list of connected clients
        server_state.add_client(client_uuid, conn_send)

        client_handler = ClientHandler(
            conn_recv, addr_recv, conn_send, addr_send, client_uuid, server_state
        )
        t = threading.Thread(target=client_handler.run)
        t.start()


if __name__ == "__main__":
    main()
