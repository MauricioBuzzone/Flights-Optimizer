import socket

class SocketBroken(Exception):
    pass

"""
This class will handle the TCP socket management, 
preventing "short reads" and "short sends."
"""
class TCPHandler:

    def __init__(self, port, ip):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.connect((ip, port))

    def read_all(client_sock, bytes_to_read):
        """
        Receives and returns byte data from the client preventing short reads.
        """
        data = b''
        while len(data) < bytes_to_read:
            bytes = client_sock.recv(bytes_to_read - len(data))
            if bytes == b'':
                raise SocketBroken()
            data += bytes
        return data

    def send_all(client_sock, msg):
        """
        Recv all n bytes to avoid short read
        """
        bytesSended = 0
        while bytesSended < len(msg):
            b = client_sock.send(msg[bytesSended:])
            if b == 0:
                raise SocketBroken()
            bytesSended += b
        return bytesSended

