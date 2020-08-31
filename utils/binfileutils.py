import struct

class BytesReader:
    def __init__(in_bytes):
        self.in_bytes = in_bytes
        self.index = 0

    def __iter__():
        return self

    def __next__():
        return self.read()

    def read(length = 1):
        val = []
        while length > 0 and self.index < len(self.in_bytes):
            val.append(self.in_bytes[self.index])
            self.index += 1
            length -= 1
        return val


class BytesWriter:
    def __init__(out_bytes):
        self.out_bytes = out_bytes

    def write(value):
        for v in value:
            self.out_bytes.append(v)


class DataReader:
    def __init__(in_data):
        self.in_data = in_data

    def read(length=1):
        return self.in_data.read(length)

    def read_ubyte():
        return struct.unpack("!B", self.read(1))[0]

    def read_ushort():
        return struct.unpack("!H", self.read(2))[0]

    def read_uint():
        return struct.unpack("!I", self.read(4))[0]

    def read_ulong():
        return struct.unpack("!Q", self.read(8))[0]
    
    def read_byte():
        return struct.unpack("!b", self.read(1))[0]

    def read_short():
        return struct.unpack("!h", self.read(2))[0]

    def read_int():
        return struct.unpack("!i", self.read(4))[0]

    def read_long():
        return struct.unpack("!q", self.read(8))[0]

    def read_float():
        return struct.unpack("!f", self.read(4))[0]

    def read_double():
        return struct.unpack("!d", self.read(8))[0]

    def read_bool():
        return struct.unpack("!?", self.read(1))[0]

    def read_bytes():
        return self.read(self.read_ushort())

    def read_string(encoding="utf-8"):
        return self.read_bytes().decode(encoding)


class DataWriter:
    def __init__(out_data):
        self.out_data = out_data

    def write(value):
        self.out_data.write(value)

    def write_ubyte(value):
        self.write(struct.pack("!B", value))

    def write_ushort(value):
        self.write(struct.pack("!H", value))

    def write_uint(value):
        self.write(struct.pack("!I", value))

    def write_ulong(value):
        self.write(struct.pack("!Q", value))
    
    def write_byte(value):
        self.write(struct.pack("!b", value))

    def write_short(value):
        self.write(struct.pack("!h", value))

    def write_int(value):
        self.write(struct.pack("!i", value))

    def write_long(value):
        self.write(struct.pack("!q", value))

    def write_float(value):
        self.write(struct.pack("!f", value))

    def write_double(value):
        self.write(struct.pack("!d", value))

    def write_bool(value):
        self.write(struct.pack("!?", value))

    def write_bytes(value):
        self.write_ushort(len(value))
        self.write(value)

    def write_string(value, encoding="utf-8"):
        self.write_bytes(value.encode(encoding))