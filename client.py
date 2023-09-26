import sys
import socket
import threading

MESSAGE_BUFFER_SIZE = 1024
SOCKET_SETUP = (socket.AF_INET, socket.SOCK_STREAM)

# Event to synchronize receiving of messages before prompting for the next input.
message_received_event = threading.Event()

# Event to signal when the user has chosen to exit, used to gracefully exit the receive handler.
user_exited_event = threading.Event()


def send_handler(client_sender_socket):
    """
    Continuously prompt the user for input and send messages to the server.

    This function runs in a loop, waiting for user input and sending the input
    as a message to the server over the provided socket. It ensures proper
    synchronization with the recv_handler, waiting for the message_received_event
    before prompting the user for the next message. The loop continues until the user
    types "/exit", signaling a desire to end the conversation.

    Parameters:
    - client_sender_socket: The socket object used to send data to the server.

    Returns:
    None
    """
    while True:
        # Wait for the message_received_event before prompting the user for input,
        # to ensure proper synchronization with recv_handler.
        message_received_event.wait()
        message_received_event.clear()

        # Prompt the user for input.
        message = input("SOCKETCHAT: ").strip()

        # If the user doesn't enter a message, set the message_received_event
        # and continue to the next iteration as there will be no server reply for an empty message.
        if not message:
            message_received_event.set()
            continue

        # Send the user's message to the server.
        client_sender_socket.sendall(message.encode())

        # If the user enters "exit", log the exit message, set the user_exited_event,
        # and break the loop to end the conversation.
        if message == "/exit":
            print("Exiting...")
            user_exited_event.set()
            break


def recv_handler(client_receiver_socket):
    """
    Continuously receive and print messages from the server.

    This function listens for incoming messages from the server
    and prints them to the console. It runs in a loop until
    the user_exited_event is set, signaling that the user has exited,
    or until the server closes the connection.

    Parameters:
    - client_receiver_socket: The socket object used to receive data
        from the server.

    Returns:
    None
    """
    while True:
        # Exit the thread gracefully if user has exited.
        if user_exited_event.is_set():
            break

        # Receive messages from the server and decode them.
        server_reply = client_receiver_socket.recv(MESSAGE_BUFFER_SIZE).decode()

        # Break the loop and exit the thread if the server closed the connection.
        if not server_reply:
            break

        # Print received messages to the console.
        print(server_reply)

        # Set the event to signal that a message has been received and printed.
        message_received_event.set()


def main():
    """
    Entry point for the client program. Initializes sockets, prompts user for
    a username, sets up threads for handling sending and receiving messages.
    """

    # Validate the number of command-line arguments.
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <host> <port>")
        sys.exit(1)

    # Extract host and port from command-line arguments.
    host, port = sys.argv[1], int(sys.argv[2])

    # Initialize and connect the sender socket.
    with socket.socket(*SOCKET_SETUP) as client_sender_socket:
        client_sender_socket.connect((host, port))

        # Initialize the receiver socket and connect it to the port assigned by the server.
        with socket.socket(*SOCKET_SETUP) as client_receiver_socket:
            receiver_port = int(client_sender_socket.recv(MESSAGE_BUFFER_SIZE).decode())
            client_receiver_socket.connect((host, int(receiver_port)))

            # Prompt the user for a non-empty username.
            while True:
                name = input("Username: ").strip()
                if name:
                    break
            client_sender_socket.sendall(f"/username {name}".encode())

            # Print the server replies, including the assigned UUID and greeting message.
            print(client_receiver_socket.recv(MESSAGE_BUFFER_SIZE).decode())
            print(client_receiver_socket.recv(MESSAGE_BUFFER_SIZE).decode())

            # Set up and start the sender thread.
            message_received_event.set()
            send_thread = threading.Thread(
                target=send_handler, args=(client_sender_socket,)
            )
            send_thread.start()

            # Use the main thread as the receiver thread.
            recv_handler(client_receiver_socket)

            # Ensure proper cleanup by waiting for the sender thread to finish before exiting.
            send_thread.join()


if __name__ == "__main__":
    main()
