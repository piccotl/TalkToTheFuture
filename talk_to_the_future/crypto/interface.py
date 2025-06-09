import crypto.parameters as params
import crypto.key_generation as kg
import crypto.public as public
import crypto.authenticated as authenticated
import secrets

def generate_keys(password: str, salt: bytes | None = None) -> tuple[dict[str, bytes], dict[str, bytes]]:

    if not salt :
        salt = kg.generate_salt()

    master_key = kg.generate_master_key(password.encode(), salt)

    password_tag = kg.derive_password_tag(master_key)

    private_key, public_key = kg.derive_encryption_keys(master_key)

    signing_key, verify_key = kg.derive_signing_keys(master_key)

    private_keys = {
        "private_key"   : private_key,
        "signing_key"   : signing_key,
    }

    public_keys = {
        "salt"          : salt,
        "password_tag"  : password_tag,
        "public_key"    : public_key,
        "verify_key"    : verify_key,
    }
    return private_keys, public_keys

def encrypt_and_sign(message: bytes, aad: bytes, receiver_pub_key: bytes, sender_sign_key: bytes) -> dict[str, bytes]:

    sym_key = authenticated.generate_sym_key()

    ciphertext = authenticated.encrypt_message(message, aad, sym_key)

    enc_sym_key = public.encrypt_sym_key(sym_key, receiver_pub_key)

    signature = public.sign_bundle(bundle=(enc_sym_key + ciphertext + aad), sign_key=sender_sign_key)

    payload = {
        "enc_sym_key"   : enc_sym_key,
        "ciphertext"    : ciphertext,
        "aad"           : aad,
        "signature"     : signature
    }

    return payload

def decrypt_and_verify(payload: dict[str, bytes], receiver_private_key: bytes) -> bytes :
    bundle = payload["enc_sym_key"] + payload["ciphertext"] + payload["aad"]

    public.verify_bundle(payload["signature"], bundle, payload["verify_key"])

    sym_key = public.decrypt_sym_key(payload["enc_sym_key"], receiver_private_key)

    plaintext = authenticated.decrypt_message(payload["ciphertext"], payload["aad"], sym_key)
    return plaintext

def generate_token() -> str:
    return secrets.token_hex(params.TOKEN_SIZE)