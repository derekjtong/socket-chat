import threading


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
