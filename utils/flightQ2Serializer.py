from utils.serializer import Serializer
from utils.protocol import TlvTypes, SIZE_LENGTH
from utils.protocol import integer_to_bytes, integer_from_bytes
from utils.protocol import string_to_bytes, string_from_bytes
from utils.protocol import float_to_bytes, float_from_bytes
from utils.protocol import code_to_bytes
from model.flight import Flight
from model.duration import Duration

class FlightQ2Serializer(Serializer):

    def make_raw_dict(self):
        return {
            TlvTypes.FLIGHT: b'',
            TlvTypes.FLIGHT_ID: b'',
            TlvTypes.FLIGHT_ORIGIN: b'',
            TlvTypes.FLIGHT_DESTINY: b'',
            TlvTypes.FLIGHT_DISTANCE: b'',
        }

    def from_raw_dict(self, raw_dict):
        return Flight(
            # mandatory:
            id=string_from_bytes(raw_dict[TlvTypes.FLIGHT_ID]),
            origin=string_from_bytes(raw_dict[TlvTypes.FLIGHT_ORIGIN]),
            destiny=string_from_bytes(raw_dict[TlvTypes.FLIGHT_DESTINY]),
            total_distance=integer_from_bytes(raw_dict[TlvTypes.FLIGHT_DISTANCE]),
            # default:
            total_fare=0.0,
            legs=[],
            flight_duration=Duration(hours=0, minutes=0),
        )

    def to_bytes(self, chunk: list):
        raw_chunk = b''

        for flight in chunk:
            raw_flight = b''
            raw_flight += string_to_bytes(flight.id, TlvTypes.FLIGHT_ID)
            raw_flight += string_to_bytes(flight.origin, TlvTypes.FLIGHT_ORIGIN)
            raw_flight += string_to_bytes(flight.destiny, TlvTypes.FLIGHT_DESTINY)
            raw_flight += integer_to_bytes(flight.total_distance, TlvTypes.FLIGHT_DISTANCE)

            raw_chunk += code_to_bytes(TlvTypes.FLIGHT)
            raw_chunk += int.to_bytes(len(raw_flight), SIZE_LENGTH, 'big') 
            raw_chunk += raw_flight

        result = code_to_bytes(TlvTypes.FLIGHT_CHUNK)
        result += int.to_bytes(len(chunk), SIZE_LENGTH, 'big') 
        result += raw_chunk

        return result