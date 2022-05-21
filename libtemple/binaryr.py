import struct


class BinaryReader():
    def __init__(self, f):
        self.f = f
        return

    def ReadInt32(self):
        v, = struct.unpack('i', self.f.read(4))
        return v

    def ReadUInt32(self):
        v, = struct.unpack('I', self.f.read(4))
        return v

    def ReadUInt64(self):
        v, = struct.unpack('L', self.f.read(8))
        return v

    def ReadByte(self):
        v, = struct.unpack('b', self.f.read(1))
        return v

    def ReadSingle(self):
        v, = struct.unpack('f', self.f.read(4))
        return v


class BinaryWriter():
    def __init__(self, f):
        self.f = f
        return

    def WriteInt32(self, v):
        self.f.write(struct.pack('i', v))
        return

    def WriteUInt32(self, v):
        self.f.write(struct.pack('I', v))
        return

    def WriteUInt64(self, v):
        self.f.write(struct.pack('L', v))
        return

    def WriteByte(self, v):
        self.f.write(struct.pack('b', v))
        return

    def WriteSingle(self, v):
        self.f.write(struct.pack('f', v))
        return