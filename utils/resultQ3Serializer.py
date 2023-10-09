from model.flight import Flight
from model.duration import Duration
from utils.resultQ3 import ResultQ3
from utils.serializer import Serializer
from utils.protocol import TlvTypes, SIZE_LENGTH
from utils.protocol import integer_to_bytes, integer_from_bytes
from utils.protocol import string_to_bytes, string_from_bytes
from utils.protocol import code_to_bytes

# ID, trayecto, escalas y duración de los 2 vuelos más rápidos para cada
#  trayecto entre todos los vuelos de 3 escalas o más.
class ResultQ3Serializer(Serializer):
    def make_raw_dict(self):
        return {
            TlvTypes.RESULT_Q3: b'', 
            TlvTypes.RESULT_Q3_ORIGIN: b'', 
            TlvTypes.RESULT_Q3_DESTINY: b'', 
            TlvTypes.RESULT_Q3_ID1: b'', 
            TlvTypes.RESULT_Q3_LEG1: [], 
            TlvTypes.RESULT_Q3_DURATION1_HOURS: b'', 
            TlvTypes.RESULT_Q3_DURATION1_MINUTES: b'', 
            TlvTypes.RESULT_Q3_ID2: b'', 
            TlvTypes.RESULT_Q3_LEG2: [], 
            TlvTypes.RESULT_Q3_DURATION2_HOURS: b'', 
            TlvTypes.RESULT_Q3_DURATION2_MINUTES: b'', 
        }

    def from_raw_dict(self, raw_dict):
        flight1 = Flight(
            id=string_from_bytes(raw_dict[TlvTypes.RESULT_Q3_ID1]),
            origin=string_from_bytes(raw_dict[TlvTypes.RESULT_Q3_ORIGIN]),
            destiny=string_from_bytes(raw_dict[TlvTypes.RESULT_Q3_DESTINY]),
            legs=[
                string_from_bytes(raw_leg) for raw_leg in raw_dict[TlvTypes.RESULT_Q3_LEG1]
            ],
            flight_duration=Duration(
                hours=integer_from_bytes(raw_dict[TlvTypes.RESULT_Q3_DURATION1_HOURS]),
                minutes=integer_from_bytes(raw_dict[TlvTypes.RESULT_Q3_DURATION1_MINUTES]),
            ),
            # default
            total_fare=0.0,
            total_distance=0,
        )

        flight2_fields = [TlvTypes.RESULT_Q3_ID2, TlvTypes.RESULT_Q3_LEG2,
                          TlvTypes.RESULT_Q3_DURATION2_HOURS, TlvTypes.RESULT_Q3_DURATION2_MINUTES]
        if all(len(raw_dict[tlvTypes]) > 0 for tlvTypes in flight2_fields):
            flight2 = Flight(
                id=string_from_bytes(raw_dict[TlvTypes.RESULT_Q3_ID2]),
                origin=string_from_bytes(raw_dict[TlvTypes.RESULT_Q3_ORIGIN]),
                destiny=string_from_bytes(raw_dict[TlvTypes.RESULT_Q3_DESTINY]),
                legs=[
                    string_from_bytes(raw_leg) for raw_leg in raw_dict[TlvTypes.RESULT_Q3_LEG2]
                ],
                flight_duration=Duration(
                    hours=integer_from_bytes(raw_dict[TlvTypes.RESULT_Q3_DURATION2_HOURS]),
                    minutes=integer_from_bytes(raw_dict[TlvTypes.RESULT_Q3_DURATION2_MINUTES]),
                ),
                # default
                total_fare=0.0,
                total_distance=0,
            )
            return ResultQ3(flight1, flight2)
        return ResultQ3(flight1)

    def to_bytes(self, chunk: list):
        raw_chunk = b''

        for resultQ3 in chunk:
            flight1 = resultQ3.fastest_flight
            flight2 = resultQ3.second_fastest_flight

            raw_result = b''
            raw_result += string_to_bytes(flight1.origin, TlvTypes.RESULT_Q3_ORIGIN)
            raw_result += string_to_bytes(flight1.origin, TlvTypes.RESULT_Q3_DESTINY)

            # flight1
            raw_result += string_to_bytes(flight1.id, TlvTypes.RESULT_Q3_ID1)
            for leg in flight1.legs:
                raw_result += string_to_bytes(leg, TlvTypes.RESULT_Q3_LEG1)
            raw_result += integer_to_bytes(flight1.flight_duration.hours, TlvTypes.RESULT_Q3_DURATION1_HOURS)
            raw_result += integer_to_bytes(flight1.flight_duration.minutes, TlvTypes.RESULT_Q3_DURATION1_MINUTES)

            # flight2
            if flight2:
                raw_result += string_to_bytes(flight2.id, TlvTypes.RESULT_Q3_ID2)
                for leg in flight2.legs:
                    raw_result += string_to_bytes(leg, TlvTypes.RESULT_Q3_LEG2)
                raw_result += integer_to_bytes(flight2.flight_duration.hours, TlvTypes.RESULT_Q3_DURATION2_HOURS)
                raw_result += integer_to_bytes(flight2.flight_duration.minutes, TlvTypes.RESULT_Q3_DURATION2_MINUTES)

            raw_chunk += code_to_bytes(TlvTypes.RESULT_Q3)
            raw_chunk += int.to_bytes(len(raw_result), SIZE_LENGTH, 'big')
            raw_chunk += raw_result

        result = code_to_bytes(TlvTypes.RESULT_Q3_CHUNK)
        result += int.to_bytes(len(chunk), SIZE_LENGTH, 'big')
        result += raw_chunk

        return result