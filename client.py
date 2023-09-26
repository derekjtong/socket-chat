import sys
import socket
import threading

message_received_event = threading.Event()


def send_handler(client_sender_socket):
    # Continuously prompt the user to enter messages to send to the server.
    while True:
        message_received_event.wait()
        message_received_event.clear()

        print("SOCKETCHAT: ", end="")
        message = input().strip()

        # If the user doesn't enter a message, skip to the next iteration.
        if not message:
            continue

        # Send the user's message to the server.
        client_sender_socket.sendall(message.encode())

        # If the user enters "exit", log the exit message and break the loop.
        if message == "/exit":
            print("Exiting...")
            break

        # Receive and print the server's reply.
        # print(client_sender_socket.recv(1024).decode())

    # Close the client socket after communication ends.
    client_sender_socket.close()


def recv_handler(client_receiver_socket):
    while True:
        server_reply = client_receiver_socket.recv(1024).decode()
        if not server_reply:
            break
        print(server_reply)
        message_received_event.set()


def main():
    # Check for the correct number of command-line arguments.
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <host> <port>")
        sys.exit(1)

    # Extract the host and port from the command-line arguments.
    host, port = sys.argv[1], int(sys.argv[2])

    # Create a new socket for the client.
    client_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the client socket to the specified server's host and port.
    client_sender_socket.connect((host, port))

    client_receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    receiver_port = int(client_sender_socket.recv(1024).decode())
    print("Assigned port:", receiver_port)

    # TODO: check if valid, else end program
    client_receiver_socket.connect((host, int(receiver_port)))
    print("Connected")

    # Prompt the user for a username.
    name = ""
    while name == "":
        name = input("Username: ").strip()

    # TODO: break the sender and receiver into separate threads
    client_sender_socket.sendall(f"/username {name}".encode())
    server_reply = client_receiver_socket.recv(1024).decode()
    print(server_reply)
    server_reply = client_receiver_socket.recv(1024).decode()
    print(server_reply)

    # Set up send and receive threads
    message_received_event.set()
    send_thread = threading.Thread(target=send_handler, args=(client_sender_socket,))
    recv_thread = threading.Thread(target=recv_handler, args=(client_receiver_socket,))
    send_thread.start()
    recv_thread.start()

    send_thread.join()
    recv_thread.join()


if __name__ == "__main__":
    main()
