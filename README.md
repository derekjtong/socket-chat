# Socket Chat

This application consists of a chat server and client, where multiple clients can communicate with each other through the server using TCP sockets. The communication protocol and logic are handled using Python's socket and threading libraries, providing the ability to handle multiple clients concurrently. The server assigns a unique UUID to each client upon connecting. Clients can use commands to list all connected clients, target a specific client by UUID, view message history, change their username, or exit the chat.

## Usage

1. Start server:
   `python3 server.py`

2. Start client:
   `python3 client.py`

Note: host and port can be changed for both in `config.py`, or as program arguments `<host> <port>`

### Get a list of connected users

1. Type `/list`

### Chat with another client

1.  Get `/list` of connected clients' UUIDs.
2.  Target client with `/target <uuid>`.
3.  Type your `<message>` and press enter.
4.  The server will send your message to the target.

### View history with another client

1. Target client with `/target <uuid>`.
2. Get `/history`

### Exit

1. `/exit`

## All Commands

Client

- `/help` - Display this help message.

- `/username <name>` - Set your username. Usage: /username <your_name>

- `/list` - List all active client IDs.

- `/history` - View your message history with your current target.

- `/target <uuid>` - Set your target for messaging and history.

- `/exit ` - Exit gracefully, alerting relevant users of departure.

Server

- `exit` - Shut down server gracefully, closing sockets and joining threads.
