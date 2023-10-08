import struct
import logging

from utils.TCPHandler import TCPHandler
from utils.protocol import TlvTypes, UnexpectedType, SIZE_LENGTH 
from utils.airportSerializer import AirportSerializer
from utils.flightSerializer import FlightSerializer

class ProtocolHandler:
    def __init__(self, socket):
        self.TCPHandler = TCPHandler(socket)
        self.airport_serializer = AirportSerializer()
        self.flight_serializer = FlightSerializer()

    def wait_confimation(self):
        type_encode_raw = self.TCPHandler.read(TlvTypes.SIZE_CODE_MSG)
        type_encode = struct.unpack('!i', type_encode_raw)[0]
        assert type_encode == TlvTypes.ACK, f'Unexpected type: expected: ACK({TlvTypes.ACK}), received {type_encode}'

    def ack(self):
        bytes = int.to_bytes(TlvTypes.ACK, TlvTypes.SIZE_CODE_MSG, 'big')
        result = self.TCPHandler.send_all(bytes)
        assert result == len(bytes), f'TCP Error: cannot send ACK'

    def send_eof(self, eof_type):
        bytes = int.to_bytes(eof_type, TlvTypes.SIZE_CODE_MSG, 'big')
        bytes += int.to_bytes(0, SIZE_LENGTH, 'big')
        result = self.TCPHandler.send_all(bytes)
        assert result == len(bytes), f'TCP Error: cannot send EOF'

    def send_airport_eof(self):
        self.send_eof(TlvTypes.AIRPORT_EOF)
        self.wait_confimation()

    def send_flight_eof(self):
        self.send_eof(TlvTypes.FLIGHT_EOF)
        self.wait_confimation()

    def send_airport(self, airports):
        bytes = self.airport_serializer.to_bytes(airports)
        result = self.TCPHandler.send_all(bytes)
        assert result == len(bytes), f'Cannot send all bytes {result} != {len(bytes)}'
        self.wait_confimation()

    def send_flight(self, flights):
        bytes = self.flight_serializer.to_bytes(flights)
        result = self.TCPHandler.send_all(bytes)
        assert result == len(bytes), f'Cannot send all bytes {result} != {len(bytes)}'
        self.wait_confimation()

    def read_tl(self):
        """
        Reads the Type and Length of TLV from self.TCPHandler and returns both.
        It reads a fixed amount of bytes (SIZE_CODE_MSG+SIZE_LENGTH)
        """
        _type_raw = self.TCPHandler.read(TlvTypes.SIZE_CODE_MSG)
        _type = struct.unpack('!i',_type_raw)[0]

        _len_raw = self.TCPHandler.read(SIZE_LENGTH)
        _len = struct.unpack('!i', _len_raw)[0]

        return _type, _len

    def read(self):
        tlv_type, tlv_len = self.read_tl()
        if self.is_airport_eof(tlv_type):
            return TlvTypes.AIRPORT_EOF, None

        if self.is_flight_eof(tlv_type):
            return TlvTypes.FLIGHT_EOF, None

        elif tlv_type == TlvTypes.AIRPORT_CHUNK:
            return TlvTypes.AIRPORT_CHUNK, self.airport_serializer.from_chunk(self.TCPHandler, header=False, n_chunks=tlv_len)

        elif tlv_type == TlvTypes.FLIGHT_CHUNK:
            return TlvTypes.FLIGHT_CHUNK, self.flight_serializer.from_chunk(self.TCPHandler, header=False, n_chunks=tlv_len)

        else:
            raise UnexpectedType()

    def is_eof(self, tlv_type):
        return tlv_type == TlvTypes.EOF
    
    def is_airport_eof(self, tlv_type):
        return tlv_type == TlvTypes.AIRPORT_EOF
    
    def is_flight_eof(self, tlv_type):
        return tlv_type == TlvTypes.FLIGHT_EOF

    def is_airports(self, tlv_type):
       return tlv_type == TlvTypes.AIRPORT_CHUNK
    
    def is_flights(self, tlv_type):
        return tlv_type == TlvTypes.FLIGHT_CHUNK
    
    def close(self):
        return
        # cerrar la conexion