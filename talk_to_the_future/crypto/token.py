import secrets

def gen_token() -> str:
    return secrets.token_hex(16)