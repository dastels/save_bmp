import board
import busio
import digitalio
from displayio import Bitmap, Palette
import adafruit_sdcard
import storage
from adafruit_bitmap_saver import save_bitmap

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
