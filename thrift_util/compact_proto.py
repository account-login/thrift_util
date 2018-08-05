import typing
import struct
import io


class ProtocolException(Exception):
    pass


class Struct:
    def __init__(self):
        self.fid2value = dict()


def _check_integer_limits(i, bits):
    if bits == 8 and (i < -128 or i > 127):
        raise ProtocolException("i8 requires -128 <= number <= 127")
    elif bits == 16 and (i < -32768 or i > 32767):
        raise ProtocolException("i16 requires -32768 <= number <= 32767")
    elif bits == 32 and (i < -2147483648 or i > 2147483647):
        raise ProtocolException("i32 requires -2147483648 <= number <= 2147483647")
    elif bits == 64 and (i < -9223372036854775808 or i > 9223372036854775807):
        raise ProtocolException("i64 requires -9223372036854775808 <= number <= 9223372036854775807")


def _make_zig_zag(n, bits):
    _check_integer_limits(n, bits)
    return (n << 1) ^ (n >> (bits - 1))


def _from_zig_zag(n):
    return (n >> 1) ^ -(n & 1)


class _FieldTypes:
    BOOL = None
    BOOLEAN_TRUE = 1
    BOOLEAN_FALSE = 2
    BYTE = 3
    I16 = 4
    I32 = 5
    I64 = 6
    DOUBLE = 7
    BINARY = 8
    LIST = 9
    SET = 10
    MAP = 11
    STRUCT = 12


class _ContainerTypes:
    BOOL = 2
    BOOLEAN_TRUE = None
    BOOLEAN_FALSE = None
    BYTE = 3
    DOUBLE = 4
    I16 = 6
    I32 = 8
    I64 = 10
    STRING = 11
    STRUCT = 12
    MAP = 13
    SET = 14
    LIST = 15


class _StructDecoder:
    def __init__(self, reader: typing.BinaryIO):
        self.reader = reader
        self.lastfid_stack = []

    def read(self, n: int):
        data = self.reader.read(n)
        if len(data) != n:
            raise EOFError('expect {} bytes'.format(n))
        return data

    def read_int(self):
        return _from_zig_zag(self.read_varint())

    def read_varint(self):
        result = 0
        shift = 0

        while True:
            x = self.read(1)
            byte = ord(x)
            result |= (byte & 0x7f) << shift
            if byte >> 7 == 0:
                return result
            shift += 7

    def _push_lastfid(self):
        self.lastfid_stack.append(0)

    def _pop_lastfid(self):
        self.lastfid_stack.pop()

    def read_field_head(self):
        b = self.read(1)[0]
        if b == 0:
            # stop
            return 0, 0

        delta = b >> 4
        type_ = b & 0b1111
        if delta == 0:
            fid = self.read_varint()
        else:
            fid = self.lastfid_stack[-1] + delta
        self.lastfid_stack[-1] = fid
        return fid, type_

    def read_size(self):
        result = self.read_varint()
        if result < 0:
            raise ProtocolException("Length < 0")
        return result

    def read_map_type(self):
        size = self.read_size()
        types = 0
        if size > 0:
            types = self.read(1)[0]

        ktype = types >> 4
        vtype = types & 0b1111
        return size, ktype, vtype

    def read_set_type(self):
        size_type = self.read(1)[0]
        size = size_type >> 4
        type_ = size_type & 0xff
        if size == 15:
            size = self.read_size()
        return size, type_

    def read_field_value(self, type_):
        return self.read_value_common(type_, _FieldTypes)

    def read_container_value(self, type_):
        return self.read_value_common(type_, _ContainerTypes)

    def read_value_common(self, type_, type_space):
        if type_ == type_space.BOOL:
            return bool(self.read(1)[0])
        elif type_ == type_space.BOOLEAN_TRUE:
            return True
        elif type_ == type_space.BOOLEAN_FALSE:
            return False
        elif type_ == type_space.BYTE:
            return self.read(1)[0]
        elif type_ in {type_space.I16, type_space.I32, type_space.I64}:
            return self.read_int()
        elif type_ == type_space.DOUBLE:
            val, = struct.unpack('<d', self.read(8))
            return val
        elif type_ == type_space.BINARY:
            size = self.read_size()
            return self.read(size)
        elif type_ == type_space.LIST:
            size, type_ = self.read_set_type()
            result = []
            for _ in range(size):
                result.append(self.read_container_value(type_))
            return result
        elif type_ == type_space.SET:
            size, type_ = self.read_set_type()
            result = set()
            for _ in range(size):
                result.add(self.read_container_value(type_))
            return result
        elif type_ == type_space.MAP:
            size, kt, vt = self.read_map_type()
            result = dict()
            for _ in range(size):
                kval = self.read_container_value(kt)
                vval = self.read_container_value(vt)
                result[kval] = vval
            return result
        elif type_ == type_space.STRUCT:
            result = dict()
            self._push_lastfid()
            while True:
                fid, type_ = self.read_field_head()
                if type_ == 0:
                    break
                result[fid] = self.read_field_value(type_)
            self._pop_lastfid()
            return result
        else:
            raise ProtocolException("unknown type: {}".format(type_))


def decode_struct(data: bytes) -> Struct:
    reader = io.BytesIO(data)
    decoder = _StructDecoder(reader)
    return decoder.read_field_value(_FieldTypes.STRUCT)
