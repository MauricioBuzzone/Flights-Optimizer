import TCPHandler 
import struct

class ProtocolHandler:

    def __init__(self, port, ip):
        self.TCPHandler = TCPHandler(port,ip)

