# FTP Protocol Design

Two TCP connections are used per session:
- **Control channel**: opened by the client to `<server>:<port>` at startup and kept open until `quit`. Carries commands and status messages.
- **Data channel**: opened fresh for each `ls`, `get`, or `put` and closed after the transfer.

## 1. What kinds of messages are exchanged on the control channel?

| Direction | Message | Meaning |
|---|---|---|
| Client -> Server | `ls <port>` | List the files in the server's directory |
| Client -> Server | `get <file> <port>` | Download `<file>` from the server |
| Client -> Server | `put <file> <port>` | Upload `<file>` to the server |
| Server -> Client | `OK` | Command accepted, server will connect to the data channel |
| Server -> Client | `ERR file not found` | `get` failed, the file does not exist on the server |
| Server -> Client | `ERR unknown command` | Command not recognized |
| Server -> Client | `Done <file> <bytes>` | `get`/`put` transfer finished |

`<port>` is the ephemeral port the client is listening on for the data channel.

## 2. How does the other side respond?

- The server replies `OK` or `ERR ...` to every command. On `ERR` the client prints the error and no data channel is opened.
- After a `get` or `put`, the server also sends `Done <file> <bytes>`, which the client reads before accepting the next command.
- The server prints `SUCCESS` or `FAILURE` for each command. After each `get`/`put` the client prints the file name and the number of bytes transferred.
- `quit`: the client closes the control socket. The server sees the connection close and waits for the next client.

## 3. What sizes/formats do the messages have?

Every message starts with a 10-byte header that holds the length of the data, padded with zeros. The actual data comes right after it (the command, status, file listing, or file bytes).

For example, `OK` is 2 bytes long, so it gets sent as `0000000002OK`.

## 4. How is a data channel set up?

1. The client creates a socket, binds it to port 0 (the OS picks an ephemeral port), and listens.
2. The client sends the command and that port on the control channel.
3. The server replies `OK`.
4. The server connects to the client's IP on that port, and the client accepts.
5. The file or listing is transferred, then both sides close the data socket.

## 5. How does the receiver know when to start/stop receiving?

- **Start:** the receiver starts reading after the data connection is accepted (after the `OK`).
- **Stop:** the 10-byte header gives the size. For `ls` and `get`, the client reads exactly that many bytes. For `put`, the server reads the header, then reads until the client closes the data connection.

## 6. How are TCP buffers kept from overflowing?

- `sendall()` keeps calling `send()` until every byte is sent.
- Receiving loops on `recv()` until all expected bytes have arrived (`recv_all` in `common.py`), so short reads are handled.
- The server reads and sends files in 4096-byte chunks instead of all at once.
- TCP flow control pauses the sender when the receiver's buffer is full.

## Diagram: `get` example

```
     Client                                         Server
       |                                              |
       |========== control connection (TCP) ========>|   (at startup)
       |                                              |
       |  bind port 0, listen on port P               |
       |---- "get file.txt P" (control) ------------->|
       |<--- "OK" (control) --------------------------|
       |                                              |
       |<========== server connects to port P ========|   (data channel)
       |<--- [size header][file bytes] (data) --------|
       |                 data channel closed          |
       |                                              |
       |<--- "Done file.txt 1234" (control) ----------|
       |  prints "file.txt : 1234 bytes transferred"  |   server prints "get SUCCESS"
       |                                              |
       |---- quit: close control connection -------->|
```

`put` follows the same steps, except the client sends `[size header][file bytes]` on the data channel. `ls` is the same, except the server sends the file listing and no `Done` message follows.
