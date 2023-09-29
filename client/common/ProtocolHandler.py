import TCPHandler 
import struct

SIZE_CODE_MSG = 4
SIZE_LENGHT = 4
SIZE_CODE_DATA = 4

AIRPORT = 0
FLIGHT = 1

FIELD = 0
VALUE = 1

class ProtocolHandler:

    def __init__(self, port, ip):
        self.TCPHandler = TCPHandler(port,ip)


    def send(self,data):
        bytes = self.serialize_message(data)
        return self.TCPHandler.sendAll(bytes)

    def read(self):
        type_encode = self.TCPHandler.read_all(SIZE_CODE_MSG)
        total_length_encode = self.TCPHandler.read_all(SIZE_LENGHT)
        type = struct.unpack('!i',type_encode)
        total_length = struct.unpack('!i',total_length_encode)

        bytes_readed = 0
        msg = {}

        while bytes_readed < total_length:
            type_field, field = self.read_data()
            type_value, value = self.read_data()

            if type_field == FIELD and type_value == VALUE:
                msg[field] = value

        return type, msg


    def read_data(self):
        type_encode = self.TCPHandler.read_all(SIZE_CODE_DATA)
        type_data = struct.unpack('!i',type_encode)
        
        length_encode = self.TCPHandler.read_all(SIZE_LENGHT)
        length = struct.unpack('!i',length_encode)
        
        data_encode = self.TCPHandler.read_all(length)
        data = data_encode.decode('utf-8')

        return type_data, data

    def serialize_message(self, msg, type):
        data = b''
        for field, value in msg.items():

            field_encode = field.encode('utf-8')
            field_size = struct.pack('!i',len(field_encode))
            data += struct.pack('!i',FIELD)
            data += field_size
            data += field_encode

            value_encode = value.encode('utf-8')
            value_size = struct.pack('!i',len(value_encode))
            data += struct.pack('!i',VALUE)
            data += value_size
            data += value_encode

        bytes = b''
        bytes += struct.pack('!i',type)
        bytes += struct.pack('!i',len(data))
        bytes += data
        return bytes


        