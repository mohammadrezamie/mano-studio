"""Generate a multi-resolution Windows ICO from the real shared Qt brand."""
import argparse
import os
from pathlib import Path
import struct

SIZES = (16, 24, 32, 48, 64, 128, 256)


def encode_ico(frames):
    """Pack top-down RGBA into 32-bit bottom-up ICO DIBs and AND masks."""
    if tuple(frames) != SIZES:
        raise ValueError("Expected all seven ordered icon resolutions")
    directory, payloads = [], []
    offset = 6 + 16 * len(SIZES)
    for size in SIZES:
        rgba = frames[size]
        if len(rgba) != size * size * 4:
            raise ValueError("Invalid RGBA frame size")
        mask_stride = ((size + 31) // 32) * 4
        xor = bytearray()
        mask = bytearray()
        for y in reversed(range(size)):
            row = bytearray(mask_stride)
            for x in range(size):
                i = 4 * (y * size + x)
                r, g, b, a = rgba[i:i+4]
                xor.extend((b, g, r, a))
                if a == 0:
                    row[x // 8] |= 1 << (7 - x % 8)
            mask.extend(row)
        header = struct.pack("<IiiHHIIiiII", 40, size, size*2, 1, 32, 0, len(xor), 0, 0, 0, 0)
        payload = header + xor + mask
        dimension = size if size < 256 else 0
        directory.append(struct.pack("<BBBBHHII", dimension, dimension, 0, 0, 1, 32, len(payload), offset))
        payloads.append(payload)
        offset += len(payload)
    return struct.pack("<HHH", 0, 1, len(SIZES)) + b"".join(directory + payloads)


def render_frames():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtGui import QImage
    from PySide6.QtWidgets import QApplication
    from ui.brand import brand_icon
    app = QApplication.instance() or QApplication([])
    icon = brand_icon("dark", True)
    frames = {}
    for size in SIZES:
        image = icon.pixmap(size, size).toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        if image.width() != size or image.height() != size or image.bytesPerLine() != size*4:
            raise ValueError("Unexpected rendered icon dimensions")
        frames[size] = bytes(image.constBits())
        alpha = frames[size][3::4]
        if not min(alpha) == 0 or not max(alpha) == 255:
            raise ValueError("Icon must contain transparent and opaque pixels")
    return frames


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    data = encode_ico(render_frames())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)


if __name__ == "__main__":
    main()
