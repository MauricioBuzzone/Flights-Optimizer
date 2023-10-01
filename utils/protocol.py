import struct

SIZE_LENGTH = 4

class TlvTypes():
    # sizes
    SIZE_CODE_MSG = 4

    # types
    EOF = 0

    AIRPORT = 1
    AIRPORT_COD = 2
    AIRPORT_LATITUDE = 3;   AIRPORT_LAT_LEN = 4
    AIRPORT_LONGITUDE = 4;  AIRPORT_LON_LEN = 4

    FLIGHT = 5
    ACK = 6

def is_eof(bytes):
    if len(bytes) == TlvTypes.SIZE_CODE_MSG:
        data = struct.unpack("!i",bytes)[0]
        return data == TlvTypes.EOF
    return False

def make_eof():
    return int.to_bytes(TlvTypes.EOF, TlvTypes.SIZE_CODE_MSG, "big")

class UnexpectedType(Exception):
    pass