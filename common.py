HEADER_SIZE = 10 # Recommended on assignment PDF

def recv_all(sock, n):
    data = b""
    while len(data) < n:
        tmpBuff = sock.recv(n - len(data))
        if not tmpBuff:
            raise ConnectionError("peer closed")
        data += tmpBuff
    return data

def send_msg(sock, data):
    if isinstance(data, str):
        data = data.encode()
    sock.sendall(str(len(data)).zfill(HEADER_SIZE).encode() + data)

def recv_msg(sock):
    return recv_all(sock, int(recv_all(sock, HEADER_SIZE)))