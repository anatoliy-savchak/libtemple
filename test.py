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

dir = r'D:\Dev.Home\GitHub\anatoliy-savchak\toee.zmod.iwd2\src\zmod_iwd2\maps\AR1000'
sector = libtemple.map.Sector(r'402653191.sec', dir)
sector.load()
sector.save(os.path.join(dir, r'402653191-2.sec'))
