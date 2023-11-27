import os
import io
import unittest

from model.flight import Flight
from model.airport import Airport
from model.duration import Duration

from utils.chunk import Chunk

from utils.serializer.flightSerializer import FlightSerializer
from utils.serializer.airportSerializer import AirportSerializer

from utils.protocol import generate_idempotency_key

class TestUtils(unittest.TestCase):
    def test_serializer_can_packet_two_airport_in_the_same_mesagge(self):
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

        ik = generate_idempotency_key()
        chunk = Chunk(ik, [airport1, airport2])

        _chunk = serializer.to_bytes(chunk)
        reader = io.BytesIO(_chunk)
        chunk = serializer.from_chunk(reader)

        _airport1 = chunk.values[0]
        _airport2 = chunk.values[1]

        assert ik.hex == chunk.id.hex

        assert airport1.cod == _airport1.cod
        assert abs(airport1.latitude-_airport1.latitude) < 1e-4
        assert abs(airport1.longitude-_airport1.longitude) < 1e-4

        assert airport2.cod == _airport2.cod
        assert abs(airport2.latitude-_airport2.latitude) < 1e-4
        assert abs(airport2.longitude-_airport2.longitude) < 1e-4

    def test_serializer_can_packet_two_flight_in_the_same_mesagge(self):
        serializer = FlightSerializer()

        flight1 = Flight(
            id='10',
            origin='CHI',
            destiny='URU',
            total_distance=3331,
            total_fare=881.123,
            legs=['BOL', 'BRA', 'ARG'],
            flight_duration = Duration(
                hours=5,
                minutes=34,
            ),
        )

        flight2 = Flight(
            id='121',
            origin='FRA',
            destiny='ENG',
            total_distance=1000,
            total_fare=41,
            legs=[],
            flight_duration = Duration(
                hours=0,
                minutes=50,
            ),
        )

        ik = generate_idempotency_key()
        chunk = Chunk(ik, [flight1, flight2])

        _chunk = serializer.to_bytes(chunk)
        reader = io.BytesIO(_chunk)
        chunk = serializer.from_chunk(reader)

        _flight1 = chunk.values[0]
        _flight2 = chunk.values[1]

        assert ik.hex == chunk.id.hex

        assert flight1.id == _flight1.id
        assert flight1.origin == _flight1.origin
        assert flight1.destiny == _flight1.destiny
        assert flight1.total_distance == _flight1.total_distance
        assert abs(flight1.total_fare-_flight1.total_fare) < 1e-4
        assert flight1.legs == _flight1.legs
        assert flight1.flight_duration.hours == _flight1.flight_duration.hours
        assert flight1.flight_duration.minutes == _flight1.flight_duration.minutes

        assert flight2.id == _flight2.id
        assert flight2.origin == _flight2.origin
        assert flight2.destiny == _flight2.destiny
        assert flight2.total_distance == _flight2.total_distance
        assert abs(flight2.total_fare-_flight2.total_fare) < 1e-4
        assert flight2.legs == _flight2.legs
        assert flight2.flight_duration.hours == _flight2.flight_duration.hours
        assert flight2.flight_duration.minutes == _flight2.flight_duration.minutes

if __name__ == '__main__':
    unittest.main()