import config
import uuid
import threading

MESSAGE_BUFFER_SIZE = config.MESSAGE_BUFFER_SIZE

# Client Commands
CMD_LIST = "/list"
CMD_EXIT = "/exit"
CMD_HISTORY = "/history"
CMD_USERNAME = "/username"
CMD_HELP = "/help"
CMD_TARGET = "/target"


class ClientHandler:
    def __init__(self, conn_recv, addr_recv, conn_send, client_uuid, server_state):
        self.conn_recv = conn_recv  # client to server socket
        self.conn_send = conn_send  # server to client socket
        self.client_uuid = client_uuid
        self.server_state = server_state
        self.ip_address, self.port = addr_recv
        self.ip_name = f"[{self.ip_address}:{self.port}]"
        self.client_name = ""
        self.thread_name = f"[{threading.get_native_id()}]"
        self.target_id = -1
        self.exit_event = threading.Event()

        self.command_handlers = {
            CMD_USERNAME: self.cmd_username,
            CMD_LIST: self.cmd_list,
            CMD_EXIT: self.cmd_exit,
            CMD_HISTORY: self.cmd_history,
            CMD_TARGET: self.cmd_target,
            CMD_HELP: self.cmd_help,
        }

    def send_to_client(self, message):
        self.conn_send.sendall(f"[SERVER] {message}".encode())

    def run(self):
        print(f"{self.thread_name} Accepting connection from {self.ip_name}")
        self.send_to_client(f"Your UUID is {self.client_uuid}")
        while True:
            client_data = self.conn_recv.recv(MESSAGE_BUFFER_SIZE).decode()
            if not client_data:
                # Client disconnected
                print(
                    f"{self.thread_name} Client {self.ip_name} disconnected unexpectedly"
                )
                self.server_state.remove_client(self.client_uuid)
                break
            if client_data[0] == "/":
                # Is command
                if self.handle_command(client_data) is False:
                    # Exited
                    break
            else:
                # Is not command, send message
                print(
                    f"{self.thread_name} Client {self.ip_name} sent message: {client_data}"
                )
                if self.target_id == -1:
                    # No target selected
                    self.send_to_client(
                        f"No target selected. Select with /target <target_uuid>"
                    )
                elif self.server_state.get_client(self.target_id) == None:
                    # Previously selected target disconnected
                    self.send_to_client(
                        f"Target exited. Select new with /target <target_uuid>"
                    )
                else:
                    # Send message to target
                    self.send_to_client("Sent")
                    # self.send_to_client(f"Sending message to {self.target_id}")
                    self.save_messages(client_data)
                    self.send_to_target(client_data)
        self.conn_recv.close()
        self.conn_send.close()

    def handle_command(self, command):
        print(f"{self.thread_name} Client {self.ip_name} used command {command}")

        for cmd, handler in self.command_handlers.items():
            if command.startswith(cmd):
                return handler(command)

        # Default handler for unrecognized commands
        self.send_to_client(f"Unrecognized command {command}")

    def save_messages(self, client_data):
        self.server_state.save_message(self.client_uuid, self.target_id, client_data)

    def cmd_username(self, command):
        self.client_name = self.get_args(command)
        self.send_to_client(f"Hello {self.client_name}")
        self.server_state.set_client_name(self.client_uuid, self.client_name)

    def cmd_list(self, command):
        values = "Active Clients:\n"
        for uuid, name in self.server_state.get_all_clients():
            values += f"    {uuid} {name}"
            if uuid == self.client_uuid:
                values += " (self)"
            values += "\n"
        self.send_to_client(values)

    def cmd_history(self, command):
        history = self.server_state.get_messages(self.client_uuid, self.target_id)
        message = f"History with {self.target_id}\n"
        if not history:
            message += "No messages."
        else:
            for item in history:
                message += item + "\n"
        self.send_to_client(message)

    def cmd_target(self, command):
        args = self.get_args(command)

        # /target
        if not args:
            if self.target_id == -1:
                self.send_to_client(
                    f"No target selected. Select with /target <target_uuid>"
                )
            else:
                self.send_to_client(f"Current target: {self.target_id}")
            return

        # /target -1 (DISCONNECTED)
        if args == -1:
            self.target_id = -1
            return

        # /target <UUID>)
        try:
            temp_target_id = uuid.UUID(args)
        except ValueError:
            self.send_to_client(
                f"Error: invalid UUID. To see connected clients, try /list"
            )
            return

        if temp_target_id == self.client_uuid:
            self.send_to_client(f"Error: cannot target self")
            return
        if self.server_state.get_client(temp_target_id):
            self.target_id = temp_target_id
            self.send_to_client(f"Connected to {self.target_id}")
        else:
            self.send_to_client(
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
        self.send_to_client(f"{help_message}")

    def get_args(self, command):
        parts = command.split(maxsplit=1)
        if len(parts) == 2:
            return parts[1]
        else:
            return False

    def cmd_exit(self, command):
        print(f"{self.thread_name} Client {self.ip_name} exited")
        self.send_to_client("Goodbye")
        if (
            self.target_id != -1
            and self.server_state.get_client(self.target_id) != None
        ):
            # Notify target of exit if they are still active
            self.server_state.get_client(self.target_id).sendall(
                f"[SERVER]: {self.client_uuid} exited".encode()
            )
        self.server_state.remove_client(self.client_uuid)
        return False

    def send_to_target(self, client_data):
        target_connection = self.server_state.get_client(self.target_id)
        if target_connection == None:
            print(f"{self.thread_name} Send error")
            return
        target_connection.sendall(f"\n{self.client_name}: {client_data}".encode())
