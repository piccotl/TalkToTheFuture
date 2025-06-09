from datetime import date

DATE_CODED_SIZE = 3

def encode_date(d: date) -> bytes:
    value = (d.year << 9) | (d.month << 5) | d.day
    return value.to_bytes(DATE_CODED_SIZE, byteorder='big')

def decode_date(b: bytes) -> date:
    if len(b) != DATE_CODED_SIZE :
        raise ValueError(f"Expected {DATE_CODED_SIZE} bytes for date encoding.")
    value = int.from_bytes(b, byteorder='big')
    day = value & 0x1f
    month = (value >> 5) & 0xf
    year = (value >> 9) & 0x7fff
    return date(year, month, day)