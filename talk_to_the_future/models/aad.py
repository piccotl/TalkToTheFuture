from datetime import date
from utils.date_codec import encode_date, decode_date, DATE_CODED_SIZE

class AAD:
    def __init__(self, sender: str, receiver: str, unlock_day: date):
        self.sender = sender
        self.receiver = receiver
        self.unlock_day = unlock_day

    def encode(self) -> bytes:
        sep = "|" # Add separator to help decoding
        sender, receiver = self.sender, self.receiver 
        encoded_date = encode_date(self.unlock_day)
        return f"{sender}{sep}{receiver}".encode() + encoded_date
    
    @classmethod
    def decode(cls, data: bytes) -> "AAD":
        sep = "|"
        text_part = data[:-DATE_CODED_SIZE] # First part is sender|receiver
        date_part = data[-DATE_CODED_SIZE:] # Last part is date (with fixed size)
        try:
            sender, receiver = text_part.decode().split(sep)
        except ValueError:
            raise ValueError("Could not split sender and receiver!")
        unlock_day = decode_date(date_part)
        return cls(sender, receiver, unlock_day)

    def __str__(self):
        return f"[From: {self.sender} | To: {self.receiver} | Unlock day: {self.unlock_day}]"