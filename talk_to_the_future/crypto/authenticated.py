import crypto.parameters as params
from nacl.utils import random
from nacl import secret

def generate_sym_key() -> bytes:
    return random(params.SYM_KEY_SIZE)

def encrypt_message(message: bytes, aad: bytes, sym_key: bytes) -> bytes:
    box = secret.Aead(sym_key)
    return box.encrypt(message, aad)

def decrypt_message(encrypted: bytes, aad: bytes, sym_key: bytes) -> bytes:
    box = secret.Aead(sym_key)
    return box.decrypt(encrypted, aad)



