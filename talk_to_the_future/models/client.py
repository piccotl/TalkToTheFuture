from models.server import Server
from models.message import AAD, Message
from utils.logger import Tracer
from datetime import date
from crypto.kdf import hash_password, generate_salt
from crypto.aead import encrypt_message, decrypt_message, gen_symmetric_key
from crypto.public_key import encrypt_sym_key

class Client: 
    def __init__(self, name: str, password: str, tr:Tracer = Tracer(trace_level='DEBUG')):
        self.name:str = name
        self.__password:bytes = password.encode() # (private attribute)
        self.server: Server = None
        self.token: bytes = None
        self.tr:Tracer = tr     # Tracer to handle general verbosity of the User
                                # 4 possible levels: ERROR, WARNING, INFO, DEBUG
    
    # Public methods -------------------------------------------------------
    def register_on(self, server: Server) -> bool:
        self.server = server

        username = self.name
        
        self.tr.debug(f'[{self.name}]: Drawing a random salt...')
        salt = generate_salt()

        self.tr.debug(f'[{self.name}]: Hashing password...')
        pwd_verifier = hash_password(self.__password, salt)
        
        self.tr.debug(f'[{self.name}]: Request a registration on {server}')
        return server.register(username, pwd_verifier, salt)

    def login_on(self, server: Server) -> bool:
        self.server = server

        self.tr.debug(f'[{self.name}]: Getting salt from {self.server}')
        salt = self.server.get_user_salt(username=self.name)                                  
        if (not salt): return False

        self.tr.debug(f'[{self.name}]: Recomputing pwd_verifier')
        pwd_verifier = hash_password(self.__password, salt)

        self.tr.debug(f'[{self.name}]: Sending login request to {self.server}')
        self.token = self.server.login(self.name, pwd_verifier)
        if not self.token:
            return False
        self.tr.debug(f'[{self.name}]: Session started with {self.server}')
        return True

    def logout(self) -> bool:
        self.tr.debug(f'[{self.name}]: Sending logout request to {self.server}')
        return self.server.logout(username=self.name, token=self.token)

    def change_password(self, new_password: str) -> bool:
        self.__password = new_password.encode()
        
        self.tr.debug(f'[{self.name}]: Drawing a random salt...')
        salt = generate_salt()

        self.tr.debug(f'[{self.name}]: Hashing password...')
        pwd_verifier = hash_password(self.__password, salt)
        
        self.tr.debug(f'[{self.name}]: Updating credentials on {self.server}')
        return self.server.update_user_credentials(self.name, self.token, pwd_verifier, salt)

    def send_message(self, data: str, receiver_name: str, unlock_day: date) -> bool:
        self.tr.debug(f'[{self.name}]: Getting {receiver_name} public key on {self.server}')
        receiver_pk = self.server.get_public_key(receiver_name)
        if not receiver_pk:
            self.tr.error(f'[{self.name}]: No public key associated to {receiver_name} on ({self.server})')
            return False

        # generate a public key to crypt the message
        self.tr.debug(f'[{self.name}]: Generating a public key')
        sym_key = gen_symmetric_key() 
        
        # Authenticated data : sender | receiver | date
        aad = AAD(sender=self.name, receiver=receiver_name, unlock_day=unlock_day)

        # encrypt message using AEAD 
        self.tr.debug(f'[{self.name}]: Encrypting message data')
        encrypted = encrypt_message(data.encode(), aad.encode(), sym_key)

        # TODO : Encrypt the AEAD encryption key using receiver public key
        self.tr.debug(f'[{self.name}]: Encrypting symmetric key')
        crypted_sym_key = encrypt_sym_key(sym_key, receiver_pk)

        # Pack message
        message = Message(encrypted, aad, crypted_sym_key)

        self.tr.debug(f'[{self.name}]: Sending message on {self.server}')
        return self.server.store_message(sender=self.name, token=self.token, message=message)

    def get_my_messages(self) -> list[AAD] | None:
        self.tr.debug(f'[{self.name}]: Requesting message metadata from {self.server}')
        return self.server.get_metadata(username=self.name, token=self.token)
    
    def read_message(self, message_id: int) -> str | None:
        self.tr.debug(f'[{self.name}]: Requesting full message (id:{message_id}) from {self.server}')
        message = self.server.get_message(username=self.name, token=self.token, message_id=message_id, no_key=False)

        if not message: 
            self.tr.error(f'[{self.name}]: Unable to read message (id:{message_id})')
            return None

        self.tr.debug(f'[{self.name}]: Decrypting message content')
        return decrypt_message(encrypted=message.data, aad=message.aad.encode(), key=message.key).decode('utf-8')
        
    def download_future_message(self, message_id: int) -> Message | None:
        self.tr.debug(f'[{self.name}]: Downloading future message (id:{message_id}) without key')
        return self.server.get_message(username=self.name, token=self.token, message_id=message_id, no_key=True)
    
    def get_message_key(self, message_id: int) -> bytes:
        self.tr.debug(f'[{self.name}]: Requesting key for message (id:{message_id})')
        return self.server.get_message_key(username=self.name, token=self.token, message_id=message_id)
    
    def __str__(self):
        return f"{self.name}"