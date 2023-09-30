import logging
from TCPHandler import TCPHandler 
from Airport import Airport
import struct

class UnexpectedType(Exception):
    pass

SIZE_LENGTH = 4
SIZE_CODE_DATA = 4

class TlvTypes():
    # sizes
    SIZE_CODE_MSG = 4

    # types

    EOF = 0

    AIRPORT = 1
    AIRPORT_COD = 2
    AIRPORT_LATITUDE = 3;   AIRPORT_LAT_LEN = 4
    AIRPORT_LONGITUDE = 4;  AIRPORT_LON_LEN = 4

    FLIGHT = 5
    ACK = 6

class ProtocolHandler:
    def __init__(self, socket):
        self.TCPHandler = TCPHandler(socket)

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

    def send_airport(self, airport):
        bytes = self.serialize_airport(airport)
        result =  self.TCPHandler.send_all(bytes)
        assert result == len(bytes)
        self.wait_confimation()

    def serialize_airport(self, airport):
        bytes = b''

        bytes += int.to_bytes(TlvTypes.AIRPORT_COD, TlvTypes.SIZE_CODE_MSG, 'big')
        bytes_cod = airport.cod.encode('utf-8')
        bytes += int.to_bytes(len(bytes_cod), SIZE_LENGTH, 'big')
        bytes += bytes_cod

        bytes += int.to_bytes(TlvTypes.AIRPORT_LATITUDE, TlvTypes.SIZE_CODE_MSG, 'big')
        bytes_lat = struct.pack('!f', airport.latitude)
        bytes += int.to_bytes(len(bytes_lat), SIZE_LENGTH, 'big')
        bytes += bytes_lat

        bytes += int.to_bytes(TlvTypes.AIRPORT_LONGITUDE, TlvTypes.SIZE_CODE_MSG, 'big')
        bytes_lon = struct.pack('!f', airport.longitude)
        bytes += int.to_bytes(len(bytes_lon), SIZE_LENGTH, 'big')
        bytes += bytes_lon

        data = b''
        data += int.to_bytes(TlvTypes.AIRPORT, TlvTypes.SIZE_CODE_MSG, 'big')
        data += int.to_bytes(len(bytes), SIZE_LENGTH, 'big')
        data += bytes
        return data

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

    def read_airport(self, tlv_len):
        assert tlv_len > 0, f'Invalid length: should be positive'

        bytes_readed = 0
        raw_airport = {
            TlvTypes.AIRPORT_COD: b'',
            TlvTypes.AIRPORT_LATITUDE: b'',
            TlvTypes.AIRPORT_LONGITUDE: b'',
        }
        while bytes_readed < tlv_len:
            field_type, length = self.read_tl()
            bytes_readed += TlvTypes.SIZE_CODE_MSG+SIZE_LENGTH
            assert bytes_readed < tlv_len, f'Invalid airport length: field {field_type} corrupted'

            raw_field = self.TCPHandler.read_all(length)
            bytes_readed += length
            assert bytes_readed <= tlv_len, f'Invalid airport length: more information received'

            raw_airport[field_type] = raw_field

        # Verification: all airports field should be received
        assert raw_airport[TlvTypes.AIRPORT_COD], "Invalid airport: no code provided"
        assert raw_airport[TlvTypes.AIRPORT_LATITUDE], "Invalid bet: no latitude provided"
        assert raw_airport[TlvTypes.AIRPORT_LONGITUDE], "Invalid bet: no longitude provided"

        return Airport(
            cod=raw_airport[TlvTypes.AIRPORT_COD].decode('utf-8'),
            latitude=struct.unpack('!f', raw_airport[TlvTypes.AIRPORT_LATITUDE]),
            longitude=struct.unpack('!f', raw_airport[TlvTypes.AIRPORT_LONGITUDE])
        )

    def read(self):
        tlv_type, tlv_len = self.read_tl()
        if tlv_type == TlvTypes.EOF:
            return TlvTypes.EOF, None
        elif tlv_type == TlvTypes.AIRPORT:
            return TlvTypes.AIRPORT, self.read_airport(tlv_len)
        # elif tlv_type == TlvTypes.CHUNK: (FUTURE)
            # ...
        else:
            raise UnexpectedType()

    def is_eof(self, tlv_type):
        return tlv_type == TlvTypes.EOF

    def close(self):
        self.eof()
        self.wait_confimation()