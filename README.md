# Socket Chat

A TCP-based chat server-client model supporting multiple users, unique IDs, and various chat commands.

## Features

1. The server can accept multiple clients and assign each of them a unique ID. When connected, the
   server sends back this ID to the client.
2. The server can accept several different commands:
   - [x] **list**: The server sends back all the active client IDs.
   - [x] **Forward ID string**: The server should be able to understand that this client wants to send
         the msg(string) to the other client with the ID that listed the command. The server should
         be able to forward the message to the target in the following format: source ID:
         message_content
   - [x] **history ID**: The server should send back the chatting history between the requested client
         and the client with the ID listed in the command.
   - [x] **exit**: The server should send back a message "Goodbye" and close the connection.

## Usage

1. Start server:
   `python3 server.py <host> <port>`

2. Start client:
   `python3 client.py <host> <port>`

 Note: host and port are optional, will default to `127.0.0.1:65432`. In case that port is occupied, change in `config.py` to reconfigure server and client simultaneously.

 Example workflow

 1. Type `/list` to get list of connected clients' UUIDs.
 2. tyep `/target <uuid>` to target a client.
 3. Type your `<message>` to send message to the targetted client.

## Commands
        /help       - Display this help message.

        /username   - Set your username. Usage: /username <your_name>

        /list       - List all active client IDs.

        /history    - View your message history with current target.

        /target     - Set your message target. Usage: /target <target_uuid>

        /exit       - Exit the client.
