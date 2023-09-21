import sys
import socket
import threading
import uuid


def link_handler(link, client, id):
    thread_id = threading.get_native_id()
    print(
        "[SERVER]: New connection from [%s:%s], created new thread [%s]"
        % (address[0], address[1], thread_id)
    )
    print(" [%s]: Client [%s:%s] connected" % (thread_id, client[0], client[1]))
    while True:
        client_data = link.recv(1024).decode()
        if client_data == "exit":
            print(
                " [%s]: Client [%s:%s] ended communication"
                % (thread_id, client[0], client[1])
            )
            break
        print(
            " [%s]: Client [%s:%s] sent message：%s"
            % (thread_id, client[0], client[1], client_data)
        )
        try:
            link.sendall(f"[{thread_id}] Server: Your UUID is {id}".encode())
        except BrokenPipeError:
            print(
                " [%s]: Client [%s:%s] forcibly closed the connection."
                % (thread_id, client[0], client[1])
            )
            break
    link.close()


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.bind((host, port))
sk.listen()

print("[SERVER]: Started listening on [%s:%s], awaiting clients..." % (host, port))

while True:
    conn, address = sk.accept()
    t = threading.Thread(target=link_handler, args=(conn, address, uuid.uuid4()))
    t.start()
