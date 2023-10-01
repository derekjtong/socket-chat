import sys
import socket
import threading
import config
import queue

# Edit in config file, server.py and client.py uses same settings
MESSAGE_BUFFER_SIZE = config.MESSAGE_BUFFER_SIZE
SOCKET_SETUP = config.SOCKET_SETUP
DEFAULT_CONNECTION = config.DEFAULT_CONNECTION

# DISABLED DUE TO BUGGINESS
# Event to synchronize receiving of messages before prompting for the next input.
# message_received_event = threading.Event()

shutdown_event = threading.Event()


def send_handler(client_sender_socket):
    """
    Continuously prompt the user for input and send messages to the server.
    """

    while not shutdown_event.is_set():
        # DISABLED DUE TO BUGGINESS
        # Wait for the message_received_event before prompting the user for input,
        # to ensure proper synchronization with recv_handler.
        # message_received_event.wait()
        # message_received_event.clear()
        # print("Your message: ", end="", flush=True)
        message = input().strip()

        try:
            client_sender_socket.sendall(message.encode())
        except BrokenPipeError:
            print("Connection to server lost.")
            break

        # If the user enters "exit", wait for server to say "Goodbye",
        # and break the loop to end the conversation.
        if message == "/exit":
            client_sender_socket.settimeout(5.0)
            try:
                print(client_sender_socket.recv(MESSAGE_BUFFER_SIZE).decode())
            except socket.timeout:
                print("No goodbye from the server :(, exiting...")
            finally:
                break


def recv_handler(client_receiver_socket):
    """
    Continuously receive and print messages from the server.
    """
    while True:
        server_reply = client_receiver_socket.recv(MESSAGE_BUFFER_SIZE).decode()

        # Server closed the connection.

        if not server_reply:
            print("Connection to server lost.")
            shutdown_event.set()
            break
        print(server_reply)
        if (
            server_reply
            == "[SERVER] Server is shutting down. Connection will be closed."
        ):
            print("shutting down recv_handler")
            shutdown_event.set()
            break
        # DISABLED DUE TO BUGGINESS
        # Set the event to signal that a message has been received and printed.
        # message_received_event.set


def main():
    """
    Entry point for the client program. Initializes sockets, prompts user for
    a username, sets up threads for handling sending and receiving messages.
    """
    if len(sys.argv) == 3:
        host, port = sys.argv[1], int(sys.argv[2])
    else:
        host, port = DEFAULT_CONNECTION

    with socket.socket(*SOCKET_SETUP) as client_sender_socket:
        client_sender_socket.connect((host, port))

        with socket.socket(*SOCKET_SETUP) as client_receiver_socket:
            # Use port assigned by server
            receiver_port = int(client_sender_socket.recv(MESSAGE_BUFFER_SIZE).decode())
            client_receiver_socket.connect((host, int(receiver_port)))

            # Prompt the user for a non-empty username.
            while True:
                name = input("Username: ").strip()
                if name:
                    break
            client_sender_socket.sendall(f"/username {name}".encode())

            # Server: your UUID is
            print(client_receiver_socket.recv(MESSAGE_BUFFER_SIZE).decode())
            # Server: hello {name}
            print(client_receiver_socket.recv(MESSAGE_BUFFER_SIZE).decode())

            # DISABLED DUE TO BUGGINESS
            # Set up and start the sender thread.
            # message_received_event.set()
            send_thread = threading.Thread(
                target=send_handler, args=(client_sender_socket,)
            )
            send_thread.start()

            # Use current thread as the receiver thread.
            recv_handler(client_receiver_socket)

            # Waiting for the sender thread to finish before exiting.
            send_thread.join()


if __name__ == "__main__":
    main()
