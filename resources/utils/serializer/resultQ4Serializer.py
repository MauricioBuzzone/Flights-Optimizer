from utils.result.resultQ4 import ResultQ4
from utils.serializer.serializer import Serializer
from utils.protocol import TlvTypes, SIZE_LENGTH
from utils.protocol import integer_to_bytes, integer_from_bytes
from utils.protocol import string_to_bytes, string_from_bytes
from utils.protocol import float_to_bytes, float_from_bytes
from utils.protocol import code_to_bytes, idempotency_key_to_bytes

class ResultQ4Serializer(Serializer):

    def make_raw_dict(self):
        return {
            TlvTypes.RESULT_Q4: b'',
            TlvTypes.RESULT_Q4_ORIGIN: b'',
            TlvTypes.RESULT_Q4_DESTINY: b'',
            TlvTypes.RESULT_Q4_FARE_AVG: b'',
            TlvTypes.RESULT_Q4_FARE_MAX: b'',
            TlvTypes.RESULT_Q4_N: b'',
        }

    def from_raw_dict(self, raw_dict):
        return ResultQ4(
            origin=string_from_bytes(raw_dict[TlvTypes.RESULT_Q4_ORIGIN]),
            destiny=string_from_bytes(raw_dict[TlvTypes.RESULT_Q4_DESTINY]),
            fare_avg=float_from_bytes(raw_dict[TlvTypes.RESULT_Q4_FARE_AVG]),
            fare_max=float_from_bytes(raw_dict[TlvTypes.RESULT_Q4_FARE_MAX]),
            n=integer_from_bytes(raw_dict[TlvTypes.RESULT_Q4_N]),
        )

    def to_bytes(self, chunk: list, idempotency_key):
        raw_chunk = b''

        for resultQ4 in chunk:
            raw_result = b''
            raw_result += string_to_bytes(resultQ4.origin, TlvTypes.RESULT_Q4_ORIGIN)
            raw_result += string_to_bytes(resultQ4.destiny, TlvTypes.RESULT_Q4_DESTINY)
            raw_result += float_to_bytes(resultQ4.fare_avg, TlvTypes.RESULT_Q4_FARE_AVG)
            raw_result += float_to_bytes(resultQ4.fare_max, TlvTypes.RESULT_Q4_FARE_MAX)
            raw_result += integer_to_bytes(resultQ4.n, TlvTypes.RESULT_Q4_N)

            raw_chunk += code_to_bytes(TlvTypes.RESULT_Q4)
            raw_chunk += int.to_bytes(len(raw_result), SIZE_LENGTH, 'big')
            raw_chunk += raw_result

        result = code_to_bytes(TlvTypes.RESULT_Q4_CHUNK)
        result += int.to_bytes(len(chunk), SIZE_LENGTH, 'big')

        result += idempotency_key_to_bytes(idempotency_key, TlvTypes.UUID)

        result += raw_chunk

        return result