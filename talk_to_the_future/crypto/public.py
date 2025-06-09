from nacl.public import SealedBox, PublicKey, PrivateKey
from nacl.signing import SigningKey, VerifyKey

def encrypt_sym_key(sym_key: bytes, public_key: bytes) -> bytes:
    pk = PublicKey(public_key)
    return SealedBox(pk).encrypt(sym_key)

def decrypt_sym_key(enc_sym_key: bytes, private_key: bytes) -> bytes:
    sk = PrivateKey(private_key)
    return SealedBox(sk).decrypt(enc_sym_key)

def sign_bundle(bundle: bytes, sign_key: bytes) -> bytes:
    return SigningKey(sign_key).sign(bundle).signature

def verify_bundle(signature: bytes, bundle: bytes, verify_key: bytes) -> None:
    try: 
        VerifyKey(verify_key).verify(smessage = bundle, signature = signature)
    except ValueError: 
        raise ValueError("Invalid signature !")