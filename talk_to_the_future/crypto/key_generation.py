import crypto.parameters as params
from nacl.utils import random
import hmac
from nacl.public import PrivateKey
from nacl.signing import SigningKey

def generate_salt() -> bytes: 
    return random(params.SALT_SIZE)

def generate_master_key(password: bytes, salt: bytes) -> bytes:
    return params.master_kdf(size=params.MASTER_KEY_SIZE,
                            password=password,
                            salt=salt,
                            opslimit=params.OPSLIMIT,
                            memlimit=params.MEMLIMIT)

def derive_password_tag(master_key: bytes) -> bytes:
    return hmac.new(digestmod=params.hash_function,
                    key=master_key,
                    msg=b'derive_password_tag').digest()[:params.TAG_SIZE]

def derive_encryption_keys(master_key: bytes) -> tuple[bytes, bytes]:
    private_key = PrivateKey(hmac.new(digestmod=params.hash_function,
                    key=master_key,
                    msg=b'derive_encryption_key').digest()[:params.PRIVATE_KEY_SIZE])
    public_key = private_key.public_key
    return private_key.encode(), public_key.encode()

def derive_signing_keys(master_key: bytes) -> tuple[bytes, bytes]:
    signing_key = SigningKey(hmac.new(digestmod=params.hash_function,
                    key=master_key,
                    msg=b'derive_signing_key').digest()[:params.SIGNING_KEY_SIZE])
    verify_key = signing_key.verify_key
    return signing_key.encode(), verify_key.encode()

