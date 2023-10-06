from utils.serializer import Serializer
from utils.protocol import TlvTypes, SIZE_LENGTH
from utils.protocol import integer_to_bytes, integer_from_bytes
from utils.protocol import string_to_bytes, string_from_bytes
from utils.protocol import float_to_bytes, float_from_bytes
from utils.protocol import code_to_bytes
from model.flight import Flight
from model.duration import Duration

class FlightQ1Serializer(Serializer):

    def make_raw_dict(self):
        return {
            TlvTypes.FLIGHT: b'',
            TlvTypes.FLIGHT_ID: b'',
            TlvTypes.FLIGHT_ORIGIN: b'',
            TlvTypes.FLIGHT_DESTINY: b'',
            TlvTypes.FLIGHT_FARE: b'',
            TlvTypes.FLIGHT_LEG: [],
            TlvTypes.FLIGHT_DURATION_HOURS: b'',
            TlvTypes.FLIGHT_DURATION_MINUTES: b'',
        }

    def from_raw_dict(self, raw_dict):
        return Flight(
            # mandatory
            id=string_from_bytes(raw_dict[TlvTypes.FLIGHT_ID]),
            origin=string_from_bytes(raw_dict[TlvTypes.FLIGHT_ORIGIN]),
            destiny=string_from_bytes(raw_dict[TlvTypes.FLIGHT_DESTINY]),
            total_fare=float_from_bytes(raw_dict[TlvTypes.FLIGHT_FARE]),
            legs=[
                string_from_bytes(raw_leg) for raw_leg in raw_dict[TlvTypes.FLIGHT_LEG]
            ],
            flight_duration=Duration(
                hours=integer_from_bytes(raw_dict[TlvTypes.FLIGHT_DURATION_HOURS]),
                minutes=integer_from_bytes(raw_dict[TlvTypes.FLIGHT_DURATION_MINUTES]),
            ),
            # default
            total_distance=0,
        )

    def to_bytes(self, chunk: list):
        raw_chunk = b''

        for flight in chunk:
            raw_flight = b''
            raw_flight += string_to_bytes(flight.id, TlvTypes.FLIGHT_ID)
            raw_flight += string_to_bytes(flight.origin, TlvTypes.FLIGHT_ORIGIN)
            raw_flight += string_to_bytes(flight.destiny, TlvTypes.FLIGHT_DESTINY)
            raw_flight += float_to_bytes(flight.total_fare, TlvTypes.FLIGHT_FARE)
            for leg in flight.legs:
                raw_flight += string_to_bytes(leg, TlvTypes.FLIGHT_LEG)
            raw_flight += integer_to_bytes(flight.flight_duration.hours, TlvTypes.FLIGHT_DURATION_HOURS)
            raw_flight += integer_to_bytes(flight.flight_duration.minutes, TlvTypes.FLIGHT_DURATION_MINUTES)

            raw_chunk += code_to_bytes(TlvTypes.FLIGHT)
            raw_chunk += int.to_bytes(len(raw_flight), SIZE_LENGTH, 'big') 
            raw_chunk += raw_flight

        result = code_to_bytes(TlvTypes.FLIGHT_CHUNK)
        result += int.to_bytes(len(chunk), SIZE_LENGTH, 'big') 
        result += raw_chunk

        return result