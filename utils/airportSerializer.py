import io
import struct
from protocol import TlvTypes, SIZE_LENGTH
from airport import Airport

class AirportSerializer():
    def from_bytes(self, bytes):
        reader = io.BytesIO(bytes)

        _tlv_type, tlv_len = self.read_tl(reader)

        bytes_readed = 0
        raw_airport = {
            TlvTypes.AIRPORT_COD: b'',
            TlvTypes.AIRPORT_LATITUDE: b'',
            TlvTypes.AIRPORT_LONGITUDE: b'',
        }

        while bytes_readed < tlv_len:
            field_type, length = self.read_tl(reader)
            bytes_readed += TlvTypes.SIZE_CODE_MSG+SIZE_LENGTH
            assert bytes_readed < tlv_len, f'Invalid airport length: field {field_type} corrupted'

            raw_field = reader.read(length)
            bytes_readed += length
            assert bytes_readed <= tlv_len, f'Invalid airport length: more information received'

            raw_airport[field_type] = raw_field

        # Verification: all airports field should be received
        assert raw_airport[TlvTypes.AIRPORT_COD], "Invalid airport: no code provided"
        assert raw_airport[TlvTypes.AIRPORT_LATITUDE], "Invalid bet: no latitude provided"
        assert raw_airport[TlvTypes.AIRPORT_LONGITUDE], "Invalid bet: no longitude provided"

        return Airport(
            cod=raw_airport[TlvTypes.AIRPORT_COD].decode('utf-8'),
            latitude=struct.unpack('!f', raw_airport[TlvTypes.AIRPORT_LATITUDE])[0],
            longitude=struct.unpack('!f', raw_airport[TlvTypes.AIRPORT_LONGITUDE])[0]
        )

    def read_tl(self, reader):
        """
        Reads the Type and Length of TLV from self.TCPHandler and returns both.
        It reads a fixed amount of bytes (SIZE_CODE_MSG+SIZE_LENGTH)
        """

        _type_raw = reader.read(TlvTypes.SIZE_CODE_MSG)
        #logging.debug(f'action: read | type: encode | result: {_type_raw}')
        _type = struct.unpack('!i',_type_raw)[0]
        #logging.debug(f'action: read | type: type | result: {_type}')

        _len_raw = reader.read(SIZE_LENGTH)
        #logging.debug(f'action: read | type: length | result: {_len_raw}')
        _len = struct.unpack('!i', _len_raw)[0]
        #logging.debug(f'action: read | type: total_length | result: {_len}')

        return _type, _len


    def to_bytes(self, airport: Airport):
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