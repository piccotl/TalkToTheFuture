from datetime import date
from utils.date_codec import encode_date, decode_date

class AAD:
    def __init__(self, sender: str, receiver: str, unlock_day: date):
        self.sender = sender
        self.receiver = receiver
        self.unlock_day = unlock_day

    def encode(self) -> bytes:
        return self.sender.encode() + self.receiver.encode() + encode_date(self.unlock_day)
    
    def __str__(self):
        return f"[From: {self.sender} | To: {self.receiver} | Unlock day: {self.unlock_day}]"

class Message:
    def __init__(self, data:bytes, aad: AAD, key:bytes):
        self.data = data
        self.aad = aad
        self.key = key

    def __str__(self):
        return f"Message: {self.aad}"
    