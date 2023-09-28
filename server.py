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

# TODO: Instead of using global variable, create a Server class and pass the object to each thread.
connected_clients = {}
connected_clients_lock = threading.Lock()

# key: uuid
# value: conn_send


class ClientHandler:
    def __init__(self, conn_recv, addr_recv, conn_send, addr_send, client_uuid):
        self.conn_recv = conn_recv
        self.addr_recv = addr_recv
        self.conn_send = conn_send
        self.addr_send = addr_send
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
        self.conn_send.sendall(message.encode())

    def run(self):
        print(
            f"[SERVER]: New connection from {self.addr_recv}, created new thread {self.thread_name}"
        )
        self.send(f"{self.thread_name} Server: Your UUID is {self.client_uuid}")
        while True:
            client_data = self.conn_recv.recv(1024).decode()
            global connected_clients
            if not client_data:
                print("Disconnected unexpectedly")
                with connected_clients_lock:
                    del connected_clients[self.client_uuid]
                break
            if client_data[0] == "/":
                if self.handle_command(client_data) is False:
                    print(f"{self.thread_name}: Client {self.addr_recv} exited")
                    with connected_clients_lock:
                        del connected_clients[self.client_uuid]
                    break
            else:
                print(
                    f"{self.thread_name}: Client {self.addr_recv} sent message: {client_data}"
                )
                if self.target_id == -1:
                    self.send(
                        f"{self.thread_name} Server: No target selected. Select with /target <target_uuid>"
                    )
                else:
                    self.send(
                        f"{self.thread_name} Server: Sending message to {self.target_id}"
                    )
                    self.send_to_target(client_data)
        self.conn_recv.close()
        self.conn_send.close()

    def handle_command(self, command):
        print(f"{self.thread_name}: Client {self.addr_recv} used command {command}")

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
        # TODO

    def cmd_target(self, command):
        global connected_clients
        args = self.get_args(command)
        if not args:
            if self.target_id == -1:
                self.send("No target selected")
            else:
                self.send(f"Current target: {self.target_id}")
            return
        try:
            self.target_id = uuid.UUID(args)
        except ValueError:
            self.send(f"Error: target not found. To see connected clients, try /list")
        else:
            if self.target_id == self.client_uuid:
                self.send(f"Error: cannot target self")
            elif self.target_id in connected_clients:
                self.send(f"Connected to {self.target_id}")
            else:
                self.send(
                    f"Error: target not found. To see connected clients, try /list"
                )

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
        parts = command.split(maxsplit=1)
        if len(parts) == 2:
            return parts[1]
        else:
            return False

    def send_to_target(self, client_data):
        try:
            target_connection = connected_clients[self.target_id]
            target_connection.sendall(f"{self.client_uuid}: {client_data}".encode())
        except Exception as e:
            print(f"Error handling client {self.target_id}: {e}")


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <host> <port>")
        sys.exit(1)

    host, port = sys.argv[1], int(sys.argv[2])

    socket_in = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_in.bind((host, port))
    socket_in.listen()

    print(f"[SERVER]: Started listening on [{host}:{port}], awaiting clients...")

    while True:
        conn_recv, addr_recv = socket_in.accept()
        client_uuid = uuid.uuid4()

        # Set up outbound socket
        socket_out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_out.bind((host, 0))
        socket_out.listen()
        conn_recv.sendall(str(socket_out.getsockname()[1]).encode())
        conn_send, addr_send = socket_out.accept()

        with connected_clients_lock:
            connected_clients[client_uuid] = conn_send
        client_handler = ClientHandler(
            conn_recv, addr_recv, conn_send, addr_send, client_uuid
        )
        t = threading.Thread(target=client_handler.run)
        t.start()


if __name__ == "__main__":
    main()
