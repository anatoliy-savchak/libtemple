import os
import libtemple.map

def generate_all_empty_secs():
    # generate simply all sectors
    dir = r'D:\Dev.Home\GitHub\anatoliy-savchak\toee.zmod.iwd2\src\zmod_iwd2\maps\test1'
    libtemple.map.Sector.generate_all_empty_sectors(dir)