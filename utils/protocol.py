import struct

SIZE_LENGTH = 4

class TlvTypes():
    # sizes
    SIZE_CODE_MSG = 4

    # types
    EOF = 0

    AIRPORT_CHUNK = 1
    AIRPORT = 2
    AIRPORT_COD = 3
    AIRPORT_LATITUDE = 4
    AIRPORT_LONGITUDE = 5

    FLIGHT_CHUNK = 6
    FLIGHT = 7
    FLIGHT_ID = 8
    FLIGHT_ORIGIN = 9
    FLIGHT_DESTINY = 10
    FLIGHT_DISTANCE = 11
    FLIGHT_FARE = 12
    FLIGHT_LEG = 13
    FLIGHT_DURATION_DAYS = 14
    FLIGHT_DURATION_HOURS = 15
    FLIGHT_DURATION_MINUTES = 16

    ACK = 17

def is_eof(bytes):
    if len(bytes) == TlvTypes.SIZE_CODE_MSG:
        data = struct.unpack("!i",bytes)[0]
        return data == TlvTypes.EOF
    return False

def make_eof():
    return code_to_bytes(TlvTypes.EOF)

def code_to_bytes(code: int):
    return int.to_bytes(code, TlvTypes.SIZE_CODE_MSG, 'big')

def integer_to_bytes(i: int, code: int):
    bytes = code_to_bytes(code)
    bytes += int.to_bytes(SIZE_LENGTH, SIZE_LENGTH, 'big')
    bytes += int.to_bytes(i, SIZE_LENGTH, 'big')
    return bytes

def integer_from_bytes(bytes_i):
    return int.from_bytes(bytes_i, 'big')

def string_to_bytes(s: str, code: int):
    bytes = code_to_bytes(code)
    bytes_s = s.encode('utf-8')
    bytes += int.to_bytes(len(bytes_s), SIZE_LENGTH, 'big')
    bytes += bytes_s
    return bytes

def string_from_bytes(bytes_s):
    return bytes_s.decode('utf-8')

def float_to_bytes(f:float, code: int):
    bytes = code_to_bytes(code)
    bytes_f = struct.pack('!f', f)
    bytes += int.to_bytes(len(bytes_f), SIZE_LENGTH, 'big')
    bytes += bytes_f
    return bytes

def float_from_bytes(bytes_f):
    return struct.unpack('!f', bytes_f)[0]


class UnexpectedType(Exception):
    pass