from nacl import utils
from nacl.pwhash import argon2id 
from hashlib import blake2b
from nacl import secret

# Master key generation ---------------
master_kdf = argon2id.kdf
MASTER_KEY_SIZE = 32
SALT_SIZE = argon2id.SALTBYTES
OPSLIMIT = argon2id.OPSLIMIT_SENSITIVE
MEMLIMIT = argon2id.MEMLIMIT_SENSITIVE
# -------------------------------------

# Keys derivation ---------------------
hash_function = blake2b
TAG_SIZE = 32
PRIVATE_KEY_SIZE = 32
SIGNING_KEY_SIZE = 32
# -------------------------------------

# Authenticated encryption ------------
SYM_KEY_SIZE = secret.Aead.KEY_SIZE
# -------------------------------------

# Session token -----------------------
TOKEN_SIZE = 16
# -------------------------------------