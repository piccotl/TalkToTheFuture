import nacl.secret
import nacl.utils


def gen_symmetric_key() -> bytes:
    return nacl.utils.random(nacl.secret.Aead.KEY_SIZE)

def encrypt_message(message: bytes, aad: bytes, key: bytes) -> bytes:
    box = nacl.secret.Aead(key)
    return box.encrypt(message, aad)

def decrypt_message(encrypted: bytes, aad: bytes, key: bytes) -> bytes:
    box = nacl.secret.Aead(key)
    return box.decrypt(encrypted, aad)