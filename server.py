import sys
import socket
import threading
import uuid
import config

from server_state import ServerState
from server_client_handler import ClientHandler

MESSAGE_BUFFER_SIZE = config.MESSAGE_BUFFER_SIZE
SOCKET_SETUP = config.SOCKET_SETUP
DEFAULT_CONNECTION = config.DEFAULT_CONNECTION


def main():
    """
    Entry point for the server program. Initializes primary listening socket
    and sets up new thread for each client that connects.
    """
    if len(sys.argv) == 3:
        host, port = sys.argv[1], int(sys.argv[2])
    else:
        host, port = DEFAULT_CONNECTION

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

        # Thread started to handle client, server continues listening
        client_handler = ClientHandler(
            conn_recv, addr_recv, conn_send, client_uuid, server_state
        )
        t = threading.Thread(target=client_handler.run)
        t.start()


if __name__ == "__main__":
    main()
