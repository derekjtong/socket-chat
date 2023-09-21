# Socket Chat

A TCP-based chat server-client model supporting multiple users, unique IDs, and various chat commands.

## Features

1. The server can accept multiple clients and assign each of them a unique ID. When connected, the
   server sends back this ID to the client.
2. The server can accept several different commands:
   1. **list**: The server sends back all the active client IDs.
   2. **Forward ID string**: The server should be able to understand that this client wants to send
      the msg(string) to the other client with the ID that listed the command. The server should
      be able to forward the message to the target in the following format: source ID:
      message_content
   3. **history ID**: The server should send back the chatting history between the requested client
      and the client with the ID listed in the command.
   4. **exit**: The server should send back a message "Goodbye" and close the connection.
      Grading Rubric

## Usage

1. Start server:
`python3 server.py <host> <port>`

2. Start client:
`python3 client.py <host> <port>`