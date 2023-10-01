import logging
from TCPHandler import TCPHandler
from airport import Airport
from protocol import TlvTypes, UnexpectedType, SIZE_LENGTH 
from airportSerializer import AirportSerializer
import struct

class ProtocolHandler:
    def __init__(self, socket):
        self.TCPHandler = TCPHandler(socket)
        self.airport_serializer = AirportSerializer()

    def wait_confimation(self):
        type_encode_raw = self.TCPHandler.read_all(TlvTypes.SIZE_CODE_MSG)
        type_encode = struct.unpack('!i', type_encode_raw)[0]
        assert type_encode == TlvTypes.ACK, f'Unexpected type: expected: ACK({TlvTypes.ACK}), received {type_encode}'

    def ack(self):
        bytes = int.to_bytes(TlvTypes.ACK, TlvTypes.SIZE_CODE_MSG, 'big')
        result = self.TCPHandler.send_all(bytes)
        assert result == len(bytes), f'TCP Error: cannot send ACK'

    def eof(self):
        bytes = int.to_bytes(TlvTypes.EOF, TlvTypes.SIZE_CODE_MSG, 'big')
        bytes += int.to_bytes(0, SIZE_LENGTH, 'big')
        result = self.TCPHandler.send_all(bytes)
        assert result == len(bytes), f'TCP Error: cannot send EOF'

    def send_airport(self, airports):
        bytes = self.airport_serializer.to_bytes(airports)
        result =  self.TCPHandler.send_all(bytes)
        assert result == len(bytes)
        self.wait_confimation()

    def read_tl(self):
        """
        Reads the Type and Length of TLV from self.TCPHandler and returns both.
        It reads a fixed amount of bytes (SIZE_CODE_MSG+SIZE_LENGTH)
        """

        _type_raw = self.TCPHandler.read_all(TlvTypes.SIZE_CODE_MSG)
        #logging.debug(f'action: read | type: encode | result: {_type_raw}')
        _type = struct.unpack('!i',_type_raw)[0]
        #logging.debug(f'action: read | type: type | result: {_type}')

        _len_raw = self.TCPHandler.read_all(SIZE_LENGTH)
        #logging.debug(f'action: read | type: length | result: {_len_raw}')
        _len = struct.unpack('!i', _len_raw)[0]
        #logging.debug(f'action: read | type: total_length | result: {_len}')

        return _type, _len

    def read(self):
        tlv_type, tlv_len = self.read_tl()
        if tlv_type == TlvTypes.EOF:
            return TlvTypes.EOF, None
        elif tlv_type == TlvTypes.AIRPORT:
            data = self.TCPHandler.read_all(tlv_len)
            data = int.to_bytes(tlv_len, SIZE_LENGTH, 'big') + data
            data = int.to_bytes(tlv_type, TlvTypes.SIZE_CODE_MSG, 'big') + data

            return TlvTypes.AIRPORT, self.airport_serializer.from_bytes(data)

        # elif tlv_type == TlvTypes.CHUNK: (FUTURE)
            # ...
        else:
            raise UnexpectedType()

    def is_eof(self, tlv_type):
        return tlv_type == TlvTypes.EOF

    def close(self):
        self.eof()
        self.wait_confimation()