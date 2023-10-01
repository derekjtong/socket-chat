import sys
import socket
import threading
import uuid
import config
import time

from server_state import ServerState
from server_client_handler import ClientHandler

# Edit in config file, server.py and client.py uses same settings
MESSAGE_BUFFER_SIZE = config.MESSAGE_BUFFER_SIZE
SOCKET_SETUP = config.SOCKET_SETUP
DEFAULT_CONNECTION = config.DEFAULT_CONNECTION


def server_input_listener(server_state):
    while True:
        user_input = input("Type 'exit' to shutdown the server:\n")
        if user_input.strip().lower() == "exit":
            server_state.set_shutdown()
            print("[SERVER] Server shutting down...")
            break


def main():
    """
    Initializes primary listening socket and sets up new thread for each client that connects.
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

    input_thread = threading.Thread(target=server_input_listener, args=(server_state,))
    input_thread.start()

    client_threads = []
    socket_in.settimeout(1)

    try:
        while not server_state.is_shutdown():
            try:
                conn_recv, addr_recv = socket_in.accept()
            except socket.timeout:
                continue
            # conn_recv, addr_recv = socket_in.accept()
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
            client_threads.append(t)
            t.start()
    finally:
        print(
            "[SERVER] Waiting for client handlers to notify clients about shutdown..."
        )
        for t in client_threads:
            t.join()  # Wait for all client handler threads to finish

        # Close sockets
        print("[SERVER] Closing client sockets...")
        for client_uuid in server_state._connected_clients.keys():
            server_state.get_client(client_uuid).close()

        print("[SERVER] Closing server socket...")
        socket_in.close()

        print("[SERVER] Server has shut down")


if __name__ == "__main__":
    main()
