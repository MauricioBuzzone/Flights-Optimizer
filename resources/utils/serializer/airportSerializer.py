from utils.serializer.serializer import Serializer
from utils.protocol import TlvTypes, SIZE_LENGTH
from utils.protocol import string_to_bytes, string_from_bytes
from utils.protocol import float_to_bytes, float_from_bytes
from utils.protocol import code_to_bytes, idempotency_key_to_bytes
from model.airport import Airport

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

    def to_bytes(self, chunk: list, idempotency_key):
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

        result += idempotency_key_to_bytes(idempotency_key, TlvTypes.UUID)

        result += raw_chunk

        return result