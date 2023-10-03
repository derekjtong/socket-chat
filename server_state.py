import threading
from datetime import datetime
from collections import defaultdict


class ServerState:
    def __init__(self):
        self._connected_clients = {}
        self._connected_clients_lock = threading.Lock()

        self._connected_client_name = {}
        self._connected_client_name_lock = threading.Lock()

        self._message_history = defaultdict(list)
        self._message_history_lock = threading.Lock()

        self._shutdown_flag = False
        self._shutdown_flag_lock = threading.Lock()

    def set_shutdown(self):
        with self._shutdown_flag_lock:
            self._shutdown_flag = True

    def is_shutdown(self):
        with self._shutdown_flag_lock:
            return self._shutdown_flag

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

    def save_message(self, client, target, msg):
        uuid1 = str(client)
        uuid2 = str(target)
        uuidkey = uuid1 + uuid2 if uuid1 < uuid2 else uuid2 + uuid1
        current_time = datetime.now().strftime("%H:%M:%S")
        with self._message_history_lock:
            self._message_history[uuidkey].append(
                f"{current_time} {self.get_client_name(client)}: {msg}"
            )

    def get_messages(self, client, target):
        uuid1 = str(client)
        uuid2 = str(target)
        uuidkey = uuid1 + uuid2 if uuid1 < uuid2 else uuid2 + uuid1
        with self._message_history_lock:
            return list(self._message_history[uuidkey])
