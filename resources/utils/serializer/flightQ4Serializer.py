from utils.serializer.serializer import Serializer
from utils.protocol import TlvTypes, SIZE_LENGTH
from utils.protocol import string_to_bytes, string_from_bytes
from utils.protocol import float_to_bytes, float_from_bytes
from utils.protocol import code_to_bytes, idempotency_key_to_bytes
from model.flight import Flight
from model.duration import Duration

class FlightQ4Serializer(Serializer):
    def __init__(self):
        super().__init__(TlvTypes.FLIGHT_CHUNK)

    def make_raw_dict(self):
        return {
            TlvTypes.FLIGHT: b'',
            TlvTypes.FLIGHT_ID: b'',
            TlvTypes.FLIGHT_ORIGIN: b'',
            TlvTypes.FLIGHT_DESTINY: b'',
            TlvTypes.FLIGHT_FARE: b'',
        }

    def from_raw_dict(self, raw_dict):
        return Flight(
            # mandatory
            id=string_from_bytes(raw_dict[TlvTypes.FLIGHT_ID]),
            origin=string_from_bytes(raw_dict[TlvTypes.FLIGHT_ORIGIN]),
            destiny=string_from_bytes(raw_dict[TlvTypes.FLIGHT_DESTINY]),
            total_fare=float_from_bytes(raw_dict[TlvTypes.FLIGHT_FARE]),
            # default
            legs=[],
            flight_duration=Duration(0, 0),
            total_distance=0,
        )

    def values_to_bytes(self, flights):
        raw_chunk = b''

        for flight in flights:
            raw_flight = b''
            raw_flight += string_to_bytes(flight.id, TlvTypes.FLIGHT_ID)
            raw_flight += string_to_bytes(flight.origin, TlvTypes.FLIGHT_ORIGIN)
            raw_flight += string_to_bytes(flight.destiny, TlvTypes.FLIGHT_DESTINY)
            raw_flight += float_to_bytes(flight.total_fare, TlvTypes.FLIGHT_FARE)

            raw_chunk += code_to_bytes(TlvTypes.FLIGHT)
            raw_chunk += int.to_bytes(len(raw_flight), SIZE_LENGTH, 'big') 
            raw_chunk += raw_flight

        return raw_chunk