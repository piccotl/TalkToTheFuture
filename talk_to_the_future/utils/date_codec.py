from datetime import date

def encode_date(d: date) -> bytes:
    value = (d.year << 9) | (d.month << 5) | d.day
    return value.to_bytes(3, byteorder='big')

def decode_date(b: bytes) -> date:
    if len(b) != 3 :
        raise ValueError("Expected 3 bytes for date encoding.")
    value = int.from_bytes(b, byteorder='big')
    day = value & 0x1f
    month = (value >> 5) & 0xf
    year = (value >> 9) & 0x7fff
    return date(year, month, day)