from nacl.pwhash import argon2id 
from nacl import secret, utils

def hash_password(password: bytes, salt: bytes) -> bytes:
    return argon2id.kdf(size=secret.SecretBox.KEY_SIZE,
                        password=password,
                        salt=salt,
                        opslimit=argon2id.OPSLIMIT_SENSITIVE,
                        memlimit=argon2id.MEMLIMIT_SENSITIVE)

def generate_salt() -> bytes: 
    return utils.random(argon2id.SALTBYTES)