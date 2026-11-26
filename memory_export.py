"""Export the current read-only memory inspection for laboratory reports."""
import csv
import io
import os
from pathlib import Path
import tempfile

from memory_inspector import memory_rows


def render(memory, known, page=None):
    rows = memory_rows(memory, known, page)
    out = io.StringIO(newline='')
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(('address_hex', 'word_hex', 'unsigned_decimal', 'signed_decimal', 'binary'))
    for address, word in rows:
        if type(word) is not int or not 0 <= word <= 65535:
            raise ValueError('Invalid 16-bit memory word')
        signed = word if word < 32768 else word - 65536
        writer.writerow((f'{address:03X}', f'{word:04X}', word, signed, f'{word:016b}'))
    return out.getvalue()


def save(path, memory, known, page=None):
    path = Path(path)
    if path.suffix.lower() != '.csv':
        raise ValueError('Use a .csv file')
    text = render(memory, known, page)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8-sig', newline='',
                                         dir=path.parent, delete=False) as stream:
            temp = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
