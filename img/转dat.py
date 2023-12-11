import struct
import numpy as np
from PIL import Image  # PIL灏辨槸pillow搴�


def color565(r, g, b):
    return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3


def main(inp, out):

    img = Image.open(inp)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img_data = np.array(img)  # 240琛�240鍒楁湁3涓� 240x240x3
    with open(out, "wb") as f:
        for line in img_data:
            for dot in line:
                f.write(struct.pack("H", color565(*dot))[::-1])


if __name__ == "__main__":
    for i in range(1, 4):
        main(
            f"G:\\05_self\\10_ESP32\\TV\\img\\pixilart-frames\\heart{i}.png",
            f"G:\\05_self\\10_ESP32\\TV\\img\\pixilart-frames\\heart{i}.dat",
        )
