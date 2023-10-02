import logging
import io
import struct
from serializer import Serializer
from protocol import TlvTypes, SIZE_LENGTH
from protocol import integer_to_bytes, integer_from_bytes
from protocol import string_to_bytes, string_from_bytes
from protocol import float_to_bytes, float_from_bytes
from protocol import code_to_bytes
from airport import Airport

class AirportSerializer(Serializer):

    def make_raw_dict(self):
        return {
            TlvTypes.AIRPORT_COD: b'',
            TlvTypes.AIRPORT_LATITUDE: b'',
            TlvTypes.AIRPORT_LONGITUDE: b'',
        }

    def from_raw_dict(self, raw_dict):

        # Verification: all airports field should be received
        assert raw_dict[TlvTypes.AIRPORT_COD], "Invalid airport: no code provided"
        assert raw_dict[TlvTypes.AIRPORT_LATITUDE], "Invalid airport: no latitude provided"
        assert raw_dict[TlvTypes.AIRPORT_LONGITUDE], "Invalid airport: no longitude provided"
        return Airport(
            cod=string_from_bytes(raw_dict[TlvTypes.AIRPORT_COD]),
            latitude=float_from_bytes(raw_dict[TlvTypes.AIRPORT_LATITUDE]),
            longitude=float_from_bytes(raw_dict[TlvTypes.AIRPORT_LONGITUDE]),
        )

    def to_bytes(self, chunk: list):
        raw_chunk = b''

        for airport in chunk:
            raw_airport = b''
            raw_airport += string_to_bytes(airport.cod, TlvTypes.AIRPORT_COD)
            raw_airport += float_to_bytes(airport.latitude, TlvTypes.AIRPORT_LATITUDE)
            raw_airport += float_to_bytes(airport.longitude, TlvTypes.AIRPORT_LONGITUDE)

            raw_chunk += code_to_bytes(TlvTypes.AIRPORT)
            raw_chunk += int.to_bytes(len(raw_airport), SIZE_LENGTH, 'big') 
            raw_chunk += raw_airport

        result = code_to_bytes(TlvTypes.AIRPORT_CHUNK)
        result += int.to_bytes(len(chunk), SIZE_LENGTH, 'big') 
        result += raw_chunk

        return result

##############################
# TESTING AIRPORT SERIALIZER #
##############################

serializer = AirportSerializer()

airport1 = Airport(
    cod='ARG',
    latitude=123.123,
    longitude=-413.3,
)

airport2 = Airport(
    cod='FRA',
    latitude=0.0,
    longitude=12,
)


chunk = serializer.to_bytes([airport1, airport2])
reader = io.BytesIO(chunk)
serial = serializer.from_chunk(reader)

_airport1 = serial[0]
_airport2 = serial[1]

assert airport1.cod == _airport1.cod
assert abs(airport1.latitude-_airport1.latitude) < 1e-4
assert abs(airport1.longitude-_airport1.longitude) < 1e-4

assert airport2.cod == _airport2.cod
assert abs(airport2.latitude-_airport2.latitude) < 1e-4
assert abs(airport2.longitude-_airport2.longitude) < 1e-4