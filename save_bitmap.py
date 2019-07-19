# The MIT License (MIT)
#
# Copyright (c) 2019 Limor Fried for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import math
import struct
import board
import busio
import digitalio
from displayio import Bitmap, Palette
import adafruit_sdcard
import storage

#pylint:disable=line-too-long,broad-except,redefined-outer-name

def swap_bytes(value):
    return ((value & 0xFF00) >> 8) | ((value & 0x00FF) << 8)

def _write_bmp_header(f, b, fs):
    f.write(bytes('BM', 'ascii'))
    f.write(struct.pack('<I', fs))
    f.write(b'\00\x00')
    f.write(b'\00\x00')
    f.write(struct.pack('<I', 54))

def _write_dib_header(f, b):
    f.write(struct.pack('<I', 40))
    f.write(struct.pack('<I', b.width))
    f.write(struct.pack('<I', b.height))
    f.write(struct.pack('<H', 1))
    f.write(struct.pack('<H', 24))
    f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

def bytes_per_row(b):
    pixel_bytes = 3 * b.width #math.ceil((24 * b.width) / 32) * 4
    padding_bytes = (4 - (pixel_bytes % 4) % 4)
    return pixel_bytes + padding_bytes

def _write_pixels(f, b, p):
    row_buffer = [0] * bytes_per_row(b)

    for y in range(b.height, 0, -1):
        buffer_index = 0
        for x in range(b.width):
            pixel = b[x, y-1]             # this is an index into the palette
            color = swap_bytes(p[pixel])  # This is a 16 bit value in r5g6b5 format
            b5 = (color & 0x001F) << 3    # extract each of the RGB tripple into it's own byte
            g6 = (color >> 3) & 0x00FC
            r5 = (color >> 8) & 0x00F8
            row_buffer[buffer_index] = b5
            buffer_index += 1
            row_buffer[buffer_index] = g6
            buffer_index += 1
            row_buffer[buffer_index] = r5
            buffer_index += 1
        f.write(bytes(row_buffer))

def save_bitmap(b, p, file_or_filename):
    if not isinstance(b, Bitmap):
        raise ValueError('bitmap')
    if not isinstance(p, Palette):
        raise ValueError('palette')
    try:
        if isinstance(file_or_filename, str):
            f = open(file_or_filename, 'wb')
        else:
            f = file_or_filename

        filesize = 54 + bitmap.height * bytes_per_row(bitmap)
        _write_bmp_header(f, b, filesize)
        _write_dib_header(f, b)
        _write_pixels(f, b, p)
    except Exception:
        print('Error saving bitmap')
        raise
    else:
        f.close()


print('Setting up SD card')
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.SD_CS)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")


WHITE = 0xFFFFFF
BLACK = 0x000000
RED = 0xFF0000
ORANGE = 0xFFA500
YELLOW = 0xFFFF00
GREEN = 0x00FF00
BLUE = 0x0000FF
PURPLE = 0x800080
PINK = 0xFFC0CB

colors = (BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, WHITE)

print('Building sample bitmap and palette')
bitmap = Bitmap(16, 16, 9)
palette = Palette(len(colors))
for i, c in enumerate(colors):
    palette[i] = c

for x in range(16):
    for y in range(16):
        if x == 0 or y == 0 or x == 15 or y == 15:
            bitmap[x, y] = 1
        elif x == y:
            bitmap[x, y] = 4
        elif x == 15 - y:
            bitmap[x, y] = 5
        else:
            bitmap[x,y] = 0

print('Saving bitmap')
save_bitmap(bitmap, palette, '/sd/test.bmp')
