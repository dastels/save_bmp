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

import struct
from displayio import Bitmap, Palette

#pylint:disable=line-too-long,broad-except,redefined-outer-name

def _write_bmp_header(f, fs):
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

def _swap_bytes(value):
    return ((value & 0xFF00) >> 8) | ((value & 0x00FF) << 8)

def _bytes_per_row(b):
    pixel_bytes = 3 * b.width
    padding_bytes = (4 - (pixel_bytes % 4)) % 4
    return pixel_bytes + padding_bytes

def _write_pixels(f, b, p):
    row_buffer = bytearray(_bytes_per_row(b))

    for y in range(b.height, 0, -1):
        buffer_index = 0
        for x in range(b.width):
            pixel = b[x, y-1]             # this is an index into the palette
            color = _swap_bytes(p[pixel])  # This is a 16 bit value in r5g6b5 format
            b5 = (color << 3) & 0x00F8    # extract each of the RGB tripple into it's own byte
            g6 = (color >> 3) & 0x00FC
            r5 = (color >> 8) & 0x00F8
            for v in (b5, g6, r5):
                row_buffer[buffer_index] = v
                buffer_index += 1
        f.write(row_buffer)

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

        filesize = 54 + b.height * _bytes_per_row(b)
        _write_bmp_header(f, filesize)
        _write_dib_header(f, b)
        _write_pixels(f, b, p)
    except Exception:
        print('Error saving bitmap')
        raise
    else:
        f.close()
