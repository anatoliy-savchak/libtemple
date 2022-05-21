import os
import libtemple.map

def test_see_sec_name():
    def ts(fn):
        loc = libtemple.map.SectorLoc.from_filename(fn)
        print(f'{loc} = {loc.to_filename()} = {loc.to_filename() == fn}')
        return
    ts('402653190.sec')
    ts('402653191.sec')
    ts('402653192.sec')
    ts('469762054.sec')
    ts('469762055.sec')
    return

def test_see_sec_name_all():
    for sy in range(1, 16):
        for sx in range(1, 16):
            fn = libtemple.map.SectorLoc(sx, sy).to_filename()
            s = libtemple.map.SectorLoc.from_filename(fn)
            if s.x != sx or s.y != sy:
                print('error!')
    return

def test_see_blocked_tiles():
    dir = r'D:\Dev.Home\GitHub\anatoliy-savchak\toee.zmod.iwd2\src\zmod_iwd2\maps\AR1000'
    sector = libtemple.map.Sector(r'402653191.sec', dir)
    sector.load()
    for y in range(libtemple.map.Sector.SECTOR_SIDE_SIZE):
        #count_blocked = sum([1 for tile in sector.tiles if tile.x == y and (tile.flags & int(libtemple.map.TileFlags.BlockMask) > 0)])
        count_blocked = 0
        for x in range(libtemple.map.Sector.SECTOR_SIDE_SIZE):
            tile = sector.tiles[y*64 + x]
            assert isinstance(tile, libtemple.map.SectorTile)
            if tile.flags & libtemple.map.TileFlags.BlockMask:
                count_blocked += 1

        print(f'{y}: {count_blocked}')
    return

def test_read_write_sec1():
    dir = r'D:\Dev.Home\GitHub\anatoliy-savchak\toee.zmod.iwd2\src\zmod_iwd2\maps\AR1000'
    sector = libtemple.map.Sector(r'402653191.sec', dir)
    sector.load()
    sector.save(os.path.join(dir, r'402653191-2.sec'))
    return

def test_gen_all():
    dir = r'D:\Dev.Home\GitHub\anatoliy-savchak\toee.zmod.iwd2\src\zmod_iwd2\maps\test1'
    for sy in range(1, 16):
        for sx in range(1, 16):
            sector = libtemple.map.Sector((sx, sy), dir)
            if True:
                for y in range(64):
                    tile = sector.tiles[y*64]
                    assert isinstance(tile, libtemple.map.SectorTile)        
                    tile.flags = tile.flags | libtemple.map.TileFlags.BlockMask
            #sector.save(r'D:\Dev.Home\GitHub\anatoliy-savchak\toee.zmod.iwd2\src\zmod_iwd2\maps\test1\469762055-2.sec')
            sector.save()
            #sector = libtemple.map.Sector('067108865.sec', dir)
    return

#test_gen_all()
#test_read_write_sec1()

#test_see_sec_name_all()

# background from 26, 30
import doc_helper
doc_helper.generate_all_empty_secs()