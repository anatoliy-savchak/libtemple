import os
import enum
import libtemple.binaryr

SECTOR_SIDE_SIZE = 64

class SectorLoc:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        return

    def pack(self):
        return self.y << 26 | self.x & 0x3FFFFFF

    @staticmethod
    def unpack(value: int):
        return SectorLoc(value & 0x3FFFFFF, value >> 26)

    def to_filename(self):
        #return f'{self.pack()}.sec'
        s = f'0x{self.y*4:x}{self.x:0>6x}'
        dec = int(s, 16)
        return f'{dec}.sec'

    @staticmethod
    def from_filename(s: str):
        s = s.lower().split('.sec', 2)[0]
        v = int(s)
        return SectorLoc.unpack(v)

    def __repr__(self) -> str:
        return f'{self.x},{self.y}'

class Sector:
    def __init__(self, file_name_or_loc_or_tuple2, dir: str):
        self.dir = dir
        self.file_name = ''
        self.sector_location = SectorLoc(-1, -1)
        if isinstance(file_name_or_loc_or_tuple2, str):
            self.sector_location = SectorLoc.from_filename(file_name_or_loc_or_tuple2)
        elif isinstance(file_name_or_loc_or_tuple2, SectorLoc):
            self.sector_location = SectorLoc(file_name_or_loc_or_tuple2.x, file_name_or_loc_or_tuple2.y)
        elif isinstance(file_name_or_loc_or_tuple2, tuple):
            self.sector_location = SectorLoc(file_name_or_loc_or_tuple2[0], file_name_or_loc_or_tuple2[1])
        else:
            raise ValueError(f'file_name_or_loc_or_tuple2: {file_name_or_loc_or_tuple2} unrecognized')

        self.file_name = self.sector_location.to_filename()

        self.tiles = []
        for y in range(SECTOR_SIDE_SIZE):
            for x in range(SECTOR_SIDE_SIZE):
                tile = SectorTile(x, y)
                self.tiles.append(tile)

        self.lights = []
        self.iPlaceholderFlags = 0x00aa0004
        self.iTileScriptsCount = 0
        self.iRooflistFlags = 1 # means to skip
        self.sectorScriptData1 = 0
        self.sectorScriptData2 = 0
        self.sectorScriptData3 = 0
        self.townmapinfo = 0
        self.aptitudeAdj = 0
        self.lightScheme = 0
        self.soundListfield00 = 0
        self.soundListfield04 = 0
        self.soundListfield08 = 0
        self.objectsblob = None
        self.iFirstObjectHeader = 0
        return

    def load(self, file_path_override: str = None):
        file_path = os.path.join(self.dir, self.file_name)
        if file_path_override:
            file_path = file_path_override
        with open(file_path, 'rb') as f:
            br = libtemple.binaryr.BinaryReader(f)
            self.lights = []
            lights_count = br.ReadUInt32()
            for light_index in range(lights_count):
                light_handle = br.ReadUInt64() #8: 0-8
                light_flags = br.ReadInt32() #4: 8-12
                light_type = br.ReadInt32() #4: 12-16 
                light_color = br.ReadUInt32() #4: 16-20
                light_field14 = br.ReadInt32() #4: 20-24
                light_position_locx = br.ReadUInt32() #4:24-28
                light_position_locy = br.ReadUInt32() #4:28-32
                light_position_off_x = br.ReadSingle() #4:32-36
                light_position_off_y = br.ReadSingle() #4:36-40
                light_offsetZ = br.ReadSingle() #4:40-44
                light_directionXasInt = br.ReadUInt32();
                light_directionYasInt = br.ReadUInt32();
                light_directionZasInt = br.ReadUInt32();
                light_range = br.ReadSingle() #4: 56-60
                light_phi = br.ReadSingle() #4: 60-64

                partSys = {}
                if light_flags & 0x10: # SectorLightFlags.PartSysPresent
                    partSys_hashCode = br.ReadInt32() #4: 64-68
                    partSys_handle = br.ReadInt32() #4: 68-72
                    partSys = {"partSys_hashCode": partSys_hashCode, "partSys_handle": partSys_handle}

                lights2 = {}
                if light_flags & 0x40: # SectorLightFlags.NightLightPresent
                    light2_type = br.ReadInt32() #4: 72-76
                    light2_color = br.ReadUInt32() #4: 76-80
                    light2_direction_X = br.ReadSingle() #4: 80-84
                    light2_direction_Y = br.ReadSingle() #4: 84-88
                    light2_direction_Z = br.ReadSingle() #4: 88-92
                    light2_range = br.ReadSingle() #4: 92-96
                    light2_phi = br.ReadSingle() #4: 96-100
                    light2_partSys_hashCode = br.ReadInt32() #4: 100-104
                    light2_partSys_handle = br.ReadInt32() #4: 104-108
                    lights2 = {
                        "light2_type": light2_type,
                        "light2_color": light2_color,
                        "light2_direction_X": light2_direction_X,
                        "light2_direction_Y": light2_direction_Y,
                        "light2_direction_Z": light2_direction_Z,
                        "light2_range": light2_range,
                        "light2_phi": light2_phi,
                        "light2_partSys_hashCode": light2_partSys_hashCode,
                        "light2_partSys_handle": light2_partSys_handle
                    }

                light = {
                    "light_handle": light_handle,
                    "light_flags": light_flags,
                    "light_type": light_type,
                    "light_color": light_color,
                    "light_field14": light_field14,
                    "light_position_locx": light_position_locx,
                    "light_position_locy": light_position_locy,
                    "light_position_off_x": light_position_off_x,
                    "light_position_off_y": light_position_off_y,
                    "light_offsetZ": light_offsetZ,
                    "light_directionXasInt": light_directionXasInt,
                    "light_directionYasInt": light_directionYasInt,
                    "light_directionZasInt": light_directionZasInt,
                    "light_range": light_range,
                    "light_phi": light_phi,
                    "partSys": partSys,
                    "lights2": lights2
                }
                self.lights.append(light)

            for y in range(64):
                for x in range(64):
                    tile = self.tiles[y*64+x]
                    assert isinstance(tile, SectorTile)

                    tile.material = TileMaterial(br.ReadByte())
                    tile.padding1 = br.ReadByte()
                    tile.padding2 = br.ReadByte()
                    tile.padding3 = br.ReadByte()
                    tile.flags = TileFlags(br.ReadUInt32())
                    tile.padding4 = br.ReadInt32()
                    tile.padding5 = br.ReadInt32()

            self.iRooflistFlags = br.ReadInt32()
            self.iPlaceholderFlags = br.ReadInt32()
            if self.iPlaceholderFlags != 0xAA0000:

                if self.iPlaceholderFlags >= 11141121:
                    self.iTileScriptsCount = br.ReadInt32()

                if self.iPlaceholderFlags >= 11141122:
                    self.sectorScriptData1 = br.ReadInt32()
                    self.sectorScriptData2 = br.ReadInt32()
                    self.sectorScriptData3 = br.ReadInt32()

                if self.iPlaceholderFlags >= 11141123:
                    self.townmapinfo = br.ReadInt32()
                    self.aptitudeAdj = br.ReadInt32()
                    self.lightScheme = br.ReadInt32()

                    self.soundListfield00 = br.ReadInt32()
                    self.soundListfield04 = br.ReadInt32()
                    self.soundListfield08 = br.ReadInt32()

            if True:
                self.iFirstObjectHeader = br.ReadInt32()
                if self.iFirstObjectHeader == 0x77:
                    f.seek(-4, 1)
                    pos = f.tell()
                    file_size = f.seek(0, 2)
                    f.seek(pos, 0)
                    objectsblob_size = file_size - pos
                    self.objectsblob = f.read(objectsblob_size)
                    objectsblob_size2 = len(self.objectsblob)
                else:
                    self.objectsblob = None
        return

    def save(self, file_path_override: str = None):
        file_path = os.path.join(self.dir, self.file_name)
        if file_path_override:
            file_path = file_path_override
        with open(file_path, 'wb') as f:
            bw = libtemple.binaryr.BinaryWriter(f)
            lights_count = len(self.lights)
            bw.WriteUInt32(lights_count)
            for light in self.lights:
                assert isinstance(light, dict)
                bw.WriteUInt64(light["light_handle"])
                bw.WriteInt32(light["light_flags"])
                bw.WriteInt32(light["light_type"])
                bw.WriteUInt32(light["light_color"])
                bw.WriteInt32(light["light_field14"])
                bw.WriteUInt32(light["light_position_locx"])
                bw.WriteUInt32(light["light_position_locy"])
                bw.WriteSingle(light["light_position_off_x"])
                bw.WriteSingle(light["light_position_off_y"])
                bw.WriteSingle(light["light_offsetZ"])
                bw.WriteUInt32(light["light_directionXasInt"])
                bw.WriteUInt32(light["light_directionYasInt"])
                bw.WriteUInt32(light["light_directionZasInt"])
                bw.WriteSingle(light["light_range"])
                bw.WriteSingle(light["light_phi"])

                light_flags = int(light["light_flags"])
                if light_flags & 0x10: # SectorLightFlags.PartSysPresent
                    partSys = light["partSys"]
                    bw.WriteInt32(partSys["partSys_hashCode"])
                    bw.WriteInt32(partSys["partSys_handle"])
                
                if light_flags & 0x40: # SectorLightFlags.NightLightPresent
                    light2 = light["lights2"]
                    bw.WriteInt32(light2["light2_type"])
                    bw.WriteUInt32(light2["light2_color"])
                    bw.WriteSingle(light2["light2_direction_X"])
                    bw.WriteSingle(light2["light2_direction_Y"])
                    bw.WriteSingle(light2["light2_direction_Z"])
                    bw.WriteSingle(light2["light2_range"])
                    bw.WriteSingle(light2["light2_phi"])
                    bw.WriteInt32(light2["light2_partSys_hashCode"])
                    bw.WriteInt32(light2["light2_partSys_handle"])


            for y in range(SECTOR_SIDE_SIZE):
                for x in range(SECTOR_SIDE_SIZE):
                    tile = self.tiles[y*SECTOR_SIDE_SIZE+x]
                    assert isinstance(tile, SectorTile)

                    bw.WriteByte(int(tile.material))
                    bw.WriteByte(tile.padding1)
                    bw.WriteByte(tile.padding2)
                    bw.WriteByte(tile.padding3)
                    bw.WriteUInt32(tile.flags)
                    bw.WriteInt32(tile.padding4)
                    bw.WriteInt32(tile.padding5)
                    f.flush()

            bw.WriteInt32(self.iRooflistFlags)
            bw.WriteInt32(self.iPlaceholderFlags)
            if self.iPlaceholderFlags != 0xAA0000:

                if self.iPlaceholderFlags >= 11141121:
                    bw.WriteInt32(self.iTileScriptsCount)

                if self.iPlaceholderFlags >= 11141122:
                    bw.WriteInt32(self.sectorScriptData1)
                    bw.WriteInt32(self.sectorScriptData2)
                    bw.WriteInt32(self.sectorScriptData3)

                if self.iPlaceholderFlags >= 11141123:
                    bw.WriteInt32(self.townmapinfo)
                    bw.WriteInt32(self.aptitudeAdj)
                    bw.WriteInt32(self.lightScheme)

                    bw.WriteInt32(self.soundListfield00)
                    bw.WriteInt32(self.soundListfield04)
                    bw.WriteInt32(self.soundListfield08)

            f.flush()
            if self.iFirstObjectHeader == 0x77:
                f.write(self.objectsblob)
            else:
                bw.WriteInt32(self.iFirstObjectHeader)
        return

    @staticmethod
    def generate_all_empty_sectors(dir: str):
        for sy in range(1, 16):
            for sx in range(1, 16):
                sector = Sector((sx, sy), dir)
                sector.save()
        return


class SectorTile:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

        self.material = TileMaterial.Dirt
        self.padding1 = 0
        self.padding2 = 0
        self.padding3 = 0
        self.flags = TileFlags.TILEFLAG_NONE
        self.padding4 = 0
        self.padding5 = 0
        return

class TileMaterial(enum.IntFlag):
    ReservedBlocked = 0
    ReservedFlyOver = 1
    Dirt = 2
    Grass = 3 # Default
    Water = 4
    DeepWater = 5
    Ice = 6
    Fire = 7
    Wood = 8
    Stone = 9
    Metal = 10
    Marsh = 11

class TileFlags(enum.IntFlag):
    TILEFLAG_NONE = 0 
    TF_Blocks = 1  # the range of flags 0x1 to 0x100 are obsolete / arcanum leftovers
    TF_Sinks = 2 
    TF_CanFlyOver = 4 
    TF_Icy = 8 
    TF_Natural = 0x10 
    TF_SoundProof = 0x20 
    TF_Indoor = 0x40 
    TF_Reflective = 0x80 
    TF_BlocksVision = 0x100  # up to here is obsolete
    BlockX0Y0 = 0x200 
    BlockX1Y0 = 0x400 
    BlockX2Y0 = 0x800 
    BlockX0Y1 = 0x1000 
    BlockX1Y1 = 0x2000 
    BlockX2Y1 = 0x4000 
    BlockX0Y2 = 0x8000 
    BlockX1Y2 = 0x10000 
    BlockX2Y2 = 0x20000 

    BlockMask = BlockX0Y0 | BlockX1Y0 | BlockX2Y0 | BlockX0Y1 | BlockX1Y1 | BlockX2Y1 | BlockX0Y2 | BlockX1Y2 | BlockX2Y2 

    FlyOverX0Y0 = 0x40000  #indices denote the subtile locations (using the same axis directions as the normal tiles)
    FlyOverX1Y0 = 0x80000 
    FlyOverX2Y0 = 0x100000 
    FlyOverX0Y1 = 0x200000 
    FlyOverX1Y1 = 0x400000 
    FlyOverX2Y1 = 0x800000 
    FlyOverX0Y2 = 0x1000000 
    FlyOverX1Y2 = 0x2000000 
    FlyOverX2Y2 = 0x4000000 

    FlyOverMask = FlyOverX0Y0 | FlyOverX1Y0 | FlyOverX2Y0 | FlyOverX0Y1 | FlyOverX1Y1 | FlyOverX2Y1 | FlyOverX0Y2 | FlyOverX1Y2 | FlyOverX2Y2 

    ProvidesCover = 0x8000000  #applies to the whole tile apparently
    TF_10000000 = 0x10000000 
    TF_20000000 = 0x20000000 
    TF_40000000 = 0x40000000 
    TF_80000000 = 0x80000000
