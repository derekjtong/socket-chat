import sys
import socket


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

name = input("Your name: ").strip()

while True:
    message = input(f"{name}: ").strip()
    if not message:
        continue
    client_socket.sendall(message.encode())

    if message == "exit":
        print("Exiting...")
        break

    server_reply = client_socket.recv(1024).decode()
    print(server_reply)
client_socket.close()
