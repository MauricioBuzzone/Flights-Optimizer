from utils.protocol import TlvTypes, SIZE_LENGTH
from utils.protocol import integer_from_bytes, code_to_bytes
from utils.protocol import bool_from_bytes, bool_to_bytes
from utils.protocol import idempotency_key_from_bytes, idempotency_key_to_bytes
from utils.protocol import workers_from_bytes, workers_to_bytes
from utils.chunk import Chunk

class Serializer:
    def __init__(self, chunk_type):
        self.chunk_type = chunk_type

    def read_t(self, reader):
        _type_raw = reader.read(TlvTypes.SIZE_CODE_MSG)
        _type = integer_from_bytes(_type_raw)
        return _type

    def read_l(self, reader):
        _len_raw = reader.read(SIZE_LENGTH)
        _len = integer_from_bytes(_len_raw)
        return _len

    def read_tl(self, reader):
        return self.read_t(reader), self.read_l(reader)

    def from_chunk(self, reader, header=True, n_chunks=None):
        if header:
            _, n_chunks = self.read_tl(reader)

        raw_idempotency_key = reader.read(TlvTypes.SIZE_UUID)
        idempotency_key = idempotency_key_from_bytes(raw_idempotency_key)

        raw_id_client = reader.read(TlvTypes.SIZE_UUID)
        id_client = idempotency_key_from_bytes(raw_id_client)

        raw_retried = reader.read(TlvTypes.SIZE_BOOL)
        retried = bool_from_bytes(raw_retried)

        raw_workers_len = self.read_l(reader)
        raw_workers = reader.read(raw_workers_len)
        workers = workers_from_bytes(raw_workers)

        _list = []
        for i in range(n_chunks):
            _tlv_type, tlv_len = self.read_tl(reader)
            obj = self.from_bytes(reader, tlv_len)
            _list.append(obj)

        return Chunk(id=idempotency_key,
                     id_client=id_client,
                     values=_list,
                     retried=retried,
                     workers=workers)

    def from_bytes(self, reader, obj_length):
        raw_dict = self.make_raw_dict()

        bytes_readed = 0
        while bytes_readed < obj_length:

            field_type = self.read_t(reader)
            bytes_readed += TlvTypes.SIZE_CODE_MSG

            length = self.read_l(reader)
            bytes_readed += SIZE_LENGTH
   
            raw_field = reader.read(length)
            bytes_readed += length

            if type(raw_dict[field_type]) == list:
                raw_dict[field_type].append(raw_field)
            else:
                raw_dict[field_type] = raw_field
        return self.from_raw_dict(raw_dict)

    def make_raw_dict(self):
        raise RuntimeError("Must be redefined")

    def from_raw_dict(self, raw_dict):
        raise RuntimeError("Must be redefined")

    def values_to_bytes(self, values:list):
        raise RuntimeError("Must be redefined")

    def to_bytes(self, chunk):
        result = code_to_bytes(self.chunk_type)
        result += int.to_bytes(len(chunk.values), SIZE_LENGTH, 'big') 

        result += idempotency_key_to_bytes(chunk.id)
        result += idempotency_key_to_bytes(chunk.id_client)
        result += bool_to_bytes(chunk.retried)
        result += workers_to_bytes(chunk.workers)

        result += self.values_to_bytes(chunk.values)
        return result