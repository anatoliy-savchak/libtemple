import os
import numpy as np
import cv2
import joblib
import math

class GroundLoc:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        return

    def pack(self):
        return self.y << 26 | self.x & 0x3FFFFFF

    @staticmethod
    def unpack(value: int):
        return GroundLoc(value & 0x3FFFFFF, value >> 26)

    def to_filename(self):
        #return f'{self.pack()}.sec'
        return f'{self.y:0>4X}{self.x:0>4X}.jpg'

    @staticmethod
    def from_filename(s: str):
        s = s.lower().split('.jpg', 2)[0]
        sy = s[:4]
        sx = s[4:]
        x = int(sx, 16)
        y = int(sy, 16)
        return GroundLoc(x, y)

    def __repr__(self) -> str:
        return f'{self.x},{self.y}'

    def as_tuple(self):
        return (self.x, self.y)


class Grounds:
    def __init__(self, dir: str, tiles_rect_tuple: tuple = None):
        self.dir = dir
        self.tiles_rect_tuple = (1, 1, 70, 70)
        self.tiles = []
        self.active_tile_rect = [-1, -1, -1, -1]
        self.preload()
        return

    def preload(self):
        for x in range(self.tiles_rect_tuple[0], self.tiles_rect_tuple[2]):
            for y in range(self.tiles_rect_tuple[1], self.tiles_rect_tuple[3]):
                tile = GroundTile((x, y))
                self.tiles.append(tile)
        return

    def load(self):
        for tile in self.tiles:
            isinstance(tile, GroundTile)
            tile.load(self.dir)
            if not tile.is_empty:
                if self.active_tile_rect[0] == -1 or tile.loc.x < self.active_tile_rect[0]:
                    self.active_tile_rect[0] = tile.loc.x
                if self.active_tile_rect[2] == -1 or tile.loc.x > self.active_tile_rect[2]:
                    self.active_tile_rect[2] = tile.loc.x
                if self.active_tile_rect[1] == -1 or tile.loc.y < self.active_tile_rect[1]:
                    self.active_tile_rect[1] = tile.loc.y
                if self.active_tile_rect[3] == -1 or tile.loc.y > self.active_tile_rect[3]:
                    self.active_tile_rect[3] = tile.loc.y
        return

    def export_active_tile_rect(self, file_path: str):
        width_tiles = self.active_tile_rect[2]-self.active_tile_rect[0] + 1
        height_tiles = self.active_tile_rect[3]-self.active_tile_rect[1] + 1
        if width_tiles <=0 or height_tiles <=0:
            raise Exception('Incorrect active_tile_rect!')

        width = 256 * width_tiles
        height = 256 * height_tiles
        image = np.zeros((height, width, 3), np.uint8)
        for tile in self.tiles:
            assert isinstance(tile, GroundTile)
            if tile.im is None: continue
            if not (self.active_tile_rect[0] <= tile.loc.x <= self.active_tile_rect[2]): continue
            if not (self.active_tile_rect[1] <= tile.loc.y <= self.active_tile_rect[3]): continue
            px = (tile.loc.x - self.active_tile_rect[0])*256
            py = (tile.loc.y - self.active_tile_rect[1])*256
            px1 = px + 256
            py1 = py + 256
            image[py:py1, px:px1,:3] = tile.im

        if file_path.lower().endswith('.jpg'):
            cv2.imwrite(file_path, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        else:
            cv2.imwrite(file_path, image)
        return

    @staticmethod
    def generate_all_blank_tiles(dir: str):
        def process(x, y):
            #v = [20 + y, 20 + x, 20+ x+ y] # BGR
            v = None
            tile = GroundTile((x, y))
            tile.create_new(v)
            tile.save(dir)
            return

        #num = 0
        #for x in range(1, 70):
        #    for y in range(1, 70):
        #        v = [20 + y, 20 + x, 20+ x+ y] # BGR
        #print(f'saved {num}')
        joblib.Parallel(n_jobs=4)(joblib.delayed(process)(x, y) for y in range(1, 70) for x in range(1, 70))
        return

    def ensure_tile(self, x: int, y: int):
        tile = next((tile for tile in self.tiles if tile.loc.x == x and tile.loc.y == y), None)
        if not tile:
            tile = GroundTile((x, y))
            self.tiles.append(tile)
        return tile

    def import_background_image(self, file_path: str, top_left_tile_coord_tuple: tuple = (26, 30)):
        bk = cv2.imread(file_path, cv2.IMREAD_COLOR)
        height, width, channels = bk.shape
        left_tile = top_left_tile_coord_tuple[0]
        top_tile = top_left_tile_coord_tuple[1]
        width_tile = math.ceil(width / 256)
        height_tile = math.ceil(height / 256)
        for y in range(height_tile):
            py = y * 256
            py1 = (y + 1) * 256
            for x in range(width_tile):
                px = x * 256
                px1 = (x + 1) * 256

                tile = self.ensure_tile(x + left_tile, y + top_tile)
                tile.create_new()
                #tile.im[:, :, 3] = bk[py:py1, px:px1, 3]
                tile.im = bk[py:py1, px:px1]
                tile.check_empty()
        return

    def save(self, skip_empty: bool = False):
        for tile in self.tiles:
            tile.save(self.dir)
        return

class GroundTile:
    def __init__(self, tuple_or_groundloc):
        x = -1
        y = -1
        if isinstance(tuple_or_groundloc, tuple):
            x, y = tuple_or_groundloc
        else:
            x, y = tuple_or_groundloc.x, tuple_or_groundloc.y

        self.loc = GroundLoc(x, y)
        self.file_exists = None
        self.is_empty = True
        self.im = None
        return

    def load(self, dir: str, show_error: bool = False):
        fp = os.path.join(dir, self.loc.to_filename())
        if not os.path.exists(fp):
            self.file_exists = False
            if show_error:
                raise Exception(f'Background tile {self.loc.x}, {self.loc.y} {fp} not found!')
            return
        self.file_exists = True
        self.im = cv2.imread(fp, cv2.IMREAD_COLOR)
        grey = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)
        c = cv2.countNonZero(grey)
        self.is_empty = c == 0
        #if not self.is_empty: print(f'{self.loc.x}, {self.loc.y} {self.loc.to_filename()} is non empty!')
        return

    def create_new(self, v = None):
        self.im = np.zeros((256, 256, 3), np.uint8)
        if not v is None:
            for x in range(0, 256):
                for y in range(0, 256):
                    self.im[y, x] = v.copy()
        self.is_empty = True
        self.file_exists = False
        return

    def save(self, dir: str):
        fn = self.loc.to_filename()
        file_path = os.path.join(dir, fn)
        if not self.is_empty:
            cv2.imwrite(file_path, self.im, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        elif os.path.exists(file_path):
            os.remove(file_path)
        #print(f'saved {self.loc.x}, {self.loc.y} {fn}')
        return file_path

    def check_empty(self):
        self.is_empty = True
        if not self.im is None:
            if self.im.size != 0:
                grey = cv2.cvtColor(self.im, cv2.COLOR_BGR2GRAY)
                c = cv2.countNonZero(grey)
                self.is_empty = c == 0
        return