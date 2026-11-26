import struct
import pytest
from installer.build_icon import SIZES, encode_ico


def frames():
    return {n: bytes((0, 0, 0, 0)) * (n*n-1) + bytes((19, 87, 223, 255)) for n in SIZES}


def test_ico_directory_and_pixel_encoding():
    data = encode_ico(frames())
    assert struct.unpack_from("<HHH", data) == (0, 1, len(SIZES))
    end = 6 + 16 * len(SIZES)
    for i, n in enumerate(SIZES):
        w, h, colors, reserved, planes, bits, length, start = struct.unpack_from("<BBBBHHII", data, 6+16*i)
        assert (w or 256, h or 256, colors, reserved, planes, bits) == (n, n, 0, 0, 1, 32)
        assert start == end
        assert struct.unpack_from("<IiiHH", data, start) == (40, n, 2*n, 1, 32)
        assert data[start+40+4*(n-1):start+40+4*n] == bytes((223, 87, 19, 255))
        mask_start = start+40+4*n*n
        bit = data[mask_start+(n-1)//8] & (1 << (7-(n-1)%8))
        assert bit == 0 and data[mask_start] & 128
        assert length == 40+4*n*n+((n+31)//32)*4*n
        end = start+length
    assert end == len(data)


def test_icon_rejects_missing_or_malformed_frames():
    with pytest.raises(ValueError):
        encode_ico({})
    bad = frames()
    bad[16] = b""
    with pytest.raises(ValueError):
        encode_ico(bad)
