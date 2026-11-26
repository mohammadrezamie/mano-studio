"""Read-only inspection of a 16-word page in the Mano Basic Computer memory."""
import re

DIGITS = str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789')


def parse_address(text):
    value = text.strip().translate(DIGITS)
    if value[:2].lower() == '0x':
        value = value[2:]
    if not re.fullmatch(r'[0-9a-fA-F]{1,3}', value):
        raise ValueError('Enter hexadecimal address 000–FFF')
    return int(value, 16)


def page_addresses(address):
    if type(address) is not int or not 0 <= address < 4096:
        raise ValueError('Memory address outside 000–FFF')
    start = address & ~15
    return tuple(range(start, start + 16))


def memory_rows(memory, known, page=None):
    """Merge touched addresses with one selected page, without mutating either."""
    if len(memory) != 4096:
        raise ValueError('Expected 4096 memory words')
    addresses = set(known)
    if page is not None:
        addresses.update(page_addresses(page))
    if any(type(a) is not int or not 0 <= a < 4096 for a in addresses):
        raise ValueError('Invalid displayed memory address')
    return [(a, memory[a]) for a in sorted(addresses)]
