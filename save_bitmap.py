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
from displayio import Bitmap, Palette

#pylint:disable=line-too-long

def _write_bmp_header(f, bitmap, fs):
    f.write(bytes('BM', 'ascii'))
    f.write(struct.pack('<I', fs))
    f.write(b'\00\x00')
    f.write(b'\00\x00')
    f.write(struct.pack('<I', 54))

def _write_dib_header(f, bitmap):
    f.write(struct.pack('<I', 40))
    f.write(struct.pack('<I', bitmap.width))
    f.write(struct.pack('<I', bitmap.height))
    f.write(struct.pack('<H', 1))
    f.write(struct.pack('<H', bitmap.depth))
    f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

def _write_pixels(f, bitmap, palette):
    bytes_per_row = math.ceil((24 * bitmap.width) / 32) * 4
    bytes_of_row_padding = (4 - (bytes_per_row % 4) % 4)

    row_buffer = [0] * (bytes_per_row + bytes_of_row_padding)
    buffer_index = 0

    for y in range(bitmap.height, 0, -1):
        for x in range(bitmap.width):
            pixel = bitmap[x][y-1]
            pixel_bytes = struct.pack('<I', palette[pixel])
            for byte_index in range(3):
                row_buffer[buffer_index] = pixel_bytes[byte_index]
                buffer_index += 1
        f.write(bytes(row_buffer))

def save_bitmap(bitmap, palette, file_or_filename):
    if not isinstance(bitmap, Bitmap):
        raise ValueError
    if not isinstance(palette, Palette):
        raise ValueError
    try:
        if isinstance(file_or_filename, str):
            f = open(file_or_filename, 'wb')
        else:
            f = file_or_filename

        filesize = 0
        _write_bmp_header(f, bitmap, filesize)
        _write_dib_header(f, bitmap)
        _write_pixels(f, bitmap, palette)
    except OSError:
        print('Cannot open ', file_or_filename)
    else:
        f.close()
