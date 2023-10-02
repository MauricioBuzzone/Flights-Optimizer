import io
import struct
from serializer import Serializer
from protocol import TlvTypes, SIZE_LENGTH
from protocol import integer_to_bytes, integer_from_bytes
from protocol import string_to_bytes, string_from_bytes
from protocol import float_to_bytes, float_from_bytes
from protocol import code_to_bytes
from flight import Flight
from duration import Duration

class FlightSerializer(Serializer):

    def make_raw_dict(self):
        return {
            TlvTypes.FLIGHT: b'',
            TlvTypes.FLIGHT_ID: b'',
            TlvTypes.FLIGHT_ORIGIN: b'',
            TlvTypes.FLIGHT_DESTINY: b'',
            TlvTypes.FLIGHT_DISTANCE: b'',
            TlvTypes.FLIGHT_FARE: b'',
            TlvTypes.FLIGHT_LEG: [],
            TlvTypes.FLIGHT_DURATION_DAYS: b'',
            TlvTypes.FLIGHT_DURATION_HOURS: b'',
            TlvTypes.FLIGHT_DURATION_MINUTES: b'',
        }

    def from_raw_dict(self, raw_dict):
        return Flight(
            id=integer_from_bytes(raw_dict[TlvTypes.FLIGHT_ID]),
            origin=string_from_bytes(raw_dict[TlvTypes.FLIGHT_ORIGIN]),
            destiny=string_from_bytes(raw_dict[TlvTypes.FLIGHT_DESTINY]),
            total_distance=integer_from_bytes(raw_dict[TlvTypes.FLIGHT_DISTANCE]),
            total_fare=float_from_bytes(raw_dict[TlvTypes.FLIGHT_FARE]),
            legs=[
                string_from_bytes(raw_leg) for raw_leg in raw_dict[TlvTypes.FLIGHT_LEG]
            ],
            flight_duration=Duration(
                days=integer_from_bytes(raw_dict[TlvTypes.FLIGHT_DURATION_DAYS]),
                hours=integer_from_bytes(raw_dict[TlvTypes.FLIGHT_DURATION_HOURS]),
                minutes=integer_from_bytes(raw_dict[TlvTypes.FLIGHT_DURATION_MINUTES]),
            ),
        )

    def to_bytes(self, chunk: list):
        raw_chunk = b''

        for flight in chunk:
            raw_flight = b''
            raw_flight += integer_to_bytes(flight.id, TlvTypes.FLIGHT_ID)
            raw_flight += string_to_bytes(flight.origin, TlvTypes.FLIGHT_ORIGIN)
            raw_flight += string_to_bytes(flight.destiny, TlvTypes.FLIGHT_DESTINY)
            raw_flight += integer_to_bytes(flight.total_distance, TlvTypes.FLIGHT_DISTANCE)
            raw_flight += float_to_bytes(flight.total_fare, TlvTypes.FLIGHT_FARE)
            for leg in flight.legs:
                raw_flight += string_to_bytes(leg, TlvTypes.FLIGHT_LEG)
            raw_flight += integer_to_bytes(flight.flight_duration.days, TlvTypes.FLIGHT_DURATION_DAYS)
            raw_flight += integer_to_bytes(flight.flight_duration.hours, TlvTypes.FLIGHT_DURATION_HOURS)
            raw_flight += integer_to_bytes(flight.flight_duration.minutes, TlvTypes.FLIGHT_DURATION_MINUTES)

            raw_chunk += code_to_bytes(TlvTypes.FLIGHT)
            raw_chunk += int.to_bytes(len(raw_flight), SIZE_LENGTH, 'big') 
            raw_chunk += raw_flight

        result = code_to_bytes(TlvTypes.FLIGHT_CHUNK)
        result += int.to_bytes(len(chunk), SIZE_LENGTH, 'big') 
        result += raw_chunk

        return result

#############################
# TESTING FLIGHT SERIALIZER #
#############################

serializer = FlightSerializer()

flight1 = Flight(
    id=10,
    origin='CHI',
    destiny='URU',
    total_distance=3331,
    total_fare=881.123,
    legs=['BOL', 'BRA', 'ARG'],
    flight_duration = Duration(
        days=1,
        hours=5,
        minutes=34,
    ),
)

flight2 = Flight(
    id=121,
    origin='FRA',
    destiny='ENG',
    total_distance=1000,
    total_fare=41,
    legs=[],
    flight_duration = Duration(
        days=0,
        hours=0,
        minutes=50,
    ),
)

chunk = serializer.to_bytes([flight1, flight2])
reader = io.BytesIO(chunk)
serial = serializer.from_chunk(reader)

_flight1 = serial[0]
_flight2 = serial[1]

assert flight1.id == _flight1.id
assert flight1.origin == _flight1.origin
assert flight1.destiny == _flight1.destiny
assert flight1.total_distance == _flight1.total_distance
assert abs(flight1.total_fare-_flight1.total_fare) < 1e-4
assert flight1.legs == _flight1.legs
assert flight1.flight_duration.days == _flight1.flight_duration.days
assert flight1.flight_duration.hours == _flight1.flight_duration.hours
assert flight1.flight_duration.minutes == _flight1.flight_duration.minutes

assert flight2.id == _flight2.id
assert flight2.origin == _flight2.origin
assert flight2.destiny == _flight2.destiny
assert flight2.total_distance == _flight2.total_distance
assert abs(flight2.total_fare-_flight2.total_fare) < 1e-4
assert flight2.legs == _flight2.legs
assert flight2.flight_duration.days == _flight2.flight_duration.days
assert flight2.flight_duration.hours == _flight2.flight_duration.hours
assert flight2.flight_duration.minutes == _flight2.flight_duration.minutes