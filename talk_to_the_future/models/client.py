from models.server import Server
from models.aad import AAD
from utils.logger import Tracer
from datetime import date
from crypto import generate_keys, encrypt_and_sign, decrypt_and_verify

class Client: 
    def __init__(self, name: str, password: str, tr:Tracer = Tracer(trace_level='DEBUG')):
        self.name:str = name
        self.server: Server = None
        
        self.__password:str = password # private attribute
        self.public_keys: dict[str, bytes] = None
        self.__private_keys: dict[str, bytes] = None # private attribute
        self.token: bytes = None

        self.tr:Tracer = tr     # Tracer to handle general verbosity of the User
                                # 4 possible levels: ERROR, WARNING, INFO, DEBUG

    
        
    # Public methods -------------------------------------------------------
    def register_on(self, server: Server) -> bool:
        self.server = server

        username = self.name
        
        self.tr.debug(f'[{self.name}]: Generating keys...')
        self.__private_keys, self.public_keys = generate_keys(self.__password)
        
        self.tr.debug(f'[{self.name}]: Request a registration on {server}')
        return server.register(username, self.public_keys)

    def login_on(self, server: Server) -> bool:
        self.server = server

        self.tr.debug(f'[{self.name}]: Getting salt from {self.server}')
        salt = self.server.get_user_salt(username=self.name)                                  
        if (not salt): return False

        self.tr.debug(f'[{self.name}]: Regenerating keys ...')
        self.__private_keys, self.public_keys = generate_keys(self.__password, salt)

        self.tr.debug(f'[{self.name}]: Sending login request to {self.server}')
        self.token = self.server.login(self.name, self.public_keys["password_tag"])
        if not self.token:
            return False
        self.tr.debug(f'[{self.name}]: Session started with {self.server}')
        return True

    def logout(self) -> bool:
        self.tr.debug(f'[{self.name}]: Sending logout request to {self.server}')
        return self.server.logout(username=self.name, token=self.token)

    def change_password(self, new_password: str) -> bool:
        self.__password = new_password
        
        self.tr.debug(f'[{self.name}]: Generating keys...')
        self.__private_keys, self.public_keys = generate_keys(self.__password)
        
        self.tr.debug(f'[{self.name}]: Updating credentials on {self.server}')
        return self.server.update_keys(self.name, self.token, self.public_keys)

    def send_message(self, content: str, receiver_name: str, unlock_day: date) -> bool:
        self.tr.debug(f'[{self.name}]: Getting {receiver_name} public key on {self.server}')
        receiver_pub_key = self.server.get_public_key(receiver_name)
        if not receiver_pub_key:
            self.tr.error(f'[{self.name}]: No public key associated to {receiver_name} on ({self.server})')
            return False
        
        # Authenticated data : sender | receiver | date
        aad = AAD(sender=self.name, receiver=receiver_name, unlock_day=unlock_day)

        # encrypt and sign the message
        self.tr.debug(f'[{self.name}]: Encrypting and signing message')
        message = encrypt_and_sign(content.encode(), aad.encode(), receiver_pub_key, self.__private_keys["signing_key"])

        self.tr.debug(f'[{self.name}]: Sending message on {self.server}')
        return self.server.send_message(sender=self.name, token=self.token, message=message)

    def get_my_messages(self) -> list[AAD] | None:
        self.tr.debug(f'[{self.name}]: Requesting message metadata from {self.server}')
        return self.server.get_metadata(username=self.name, token=self.token)
    
    def read_message(self, message_id: int) -> str | None:
        self.tr.debug(f'[{self.name}]: Requesting full message (id:{message_id}) from {self.server}')
        encoded_msg = self.server.get_message(username=self.name, token=self.token, message_id=message_id, no_key=False)

        if not encoded_msg: 
            self.tr.error(f'[{self.name}]: Unable to read message (id:{message_id})')
            return None

        self.tr.debug(f'[{self.name}]: Decrypting message content')
        return decrypt_and_verify(payload=encoded_msg, receiver_private_key=self.__private_keys["private_key"]).decode('utf-8')
        
    def download_future_message(self, message_id: int) -> dict[str, bytes] | None:
        self.tr.debug(f'[{self.name}]: Downloading future message (id:{message_id}) without key')
        return self.server.get_message(username=self.name, token=self.token, message_id=message_id, no_key=True)
    
    def get_msg_enc_sym_key(self, message_id: int) -> bytes | None:
        self.tr.debug(f'[{self.name}]: Requesting key for message (id:{message_id})')
        enc_sym_key = self.server.get_message_key(username=self.name, token=self.token, message_id=message_id)

        if not enc_sym_key: 
            self.tr.error(f'[{self.name}]: Unable to get symmetric key for this message (id:{message_id})')
            return None
        return enc_sym_key

    def __str__(self):
        return f"{self.name}"