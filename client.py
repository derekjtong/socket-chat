import sys
import socket
import threading

message_received_event = threading.Event()
user_exited_event = threading.Event()


def send_handler(client_sender_socket):
    while True:
        # Needed or else user prompt "SOCKETCHAT:" prints on same line as server reply
        message_received_event.wait()
        message_received_event.clear()

        message = input("SOCKETCHAT: ").strip()

        # If the user doesn't enter a message, skip to the next iteration.
        if not message:
            # Must set event because server will not reply
            message_received_event.set()
            continue

        # Send the user's message to the server.
        client_sender_socket.sendall(message.encode())

        # If the user enters "exit", log the exit message and break the loop.
        if message == "/exit":
            print("Exiting...")
            user_exited_event.set()
            break

    client_sender_socket.close()


def recv_handler(client_receiver_socket):
    while True:
        if user_exited_event.is_set():
            break
        server_reply = client_receiver_socket.recv(1024).decode()
        if not server_reply:
            break
        print(server_reply)
        message_received_event.set()


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <host> <port>")
        sys.exit(1)

    # Extract the host and port from the command-line arguments.
    host, port = sys.argv[1], int(sys.argv[2])

    # New socket for outgoing messages.
    client_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the client socket to the specified server's host and port.
    client_sender_socket.connect((host, port))

    # New socket for incoming messages.
    client_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Receive port assigned by server
    receiver_port = int(client_sender_socket.recv(1024).decode())

    # Connect to port assigned by server.
    client_receiver_socket.connect((host, int(receiver_port)))

    # Prompt the user for a username.
    name = ""
    while name == "":
        name = input("Username: ").strip()
    client_sender_socket.sendall(f"/username {name}".encode())

    # Receive UUID
    server_reply = client_receiver_socket.recv(1024).decode()
    print(server_reply)

    # Hello {username}
    server_reply = client_receiver_socket.recv(1024).decode()
    print(server_reply)

    # Set up send and receive threads
    message_received_event.set()
    send_thread = threading.Thread(target=send_handler, args=(client_sender_socket,))
    send_thread.start()

    # Run receiver in main thread
    recv_handler(client_receiver_socket)

    # Wait for thread to close before ending
    send_thread.join()


if __name__ == "__main__":
    main()
