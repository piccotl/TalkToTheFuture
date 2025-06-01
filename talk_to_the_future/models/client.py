from models.user_infos import UserInfos
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
        self.tr:Tracer = tr     # Tracer to handle general verbosity of the User
                                # 4 possible levels: ERROR, WARNING, INFO, DEBUG
    
    # Private methods -------------------------------------------
    def __gen_public_infos(self) -> UserInfos:

        self.tr.debug(f'[{self.name}]: Drawing a random salt...')
        salt = generate_salt()

        self.tr.debug(f'[{self.name}]: Hashing password...')
        pwd_verifier = hash_password(self.__password, salt)

        return UserInfos(self.name, pwd_verifier, salt)

    # Public methods -------------------------------------------------------
    def register_on(self, server: Server) -> bool:
        public_infos = self.__gen_public_infos()
        self.tr.debug(f'[{self.name}]: Request a registration on {server}')
        return server.register(public_infos)

    def login_on(self, server: Server) -> bool:
        self.tr.debug(f'[{self.name}]: Getting salt from {server}')
        salt = server.get_user_salt(self.name)                                  
        if (not salt): return False

        self.tr.debug(f'[{self.name}]: Recomputing pwd_verifier')
        pwd_verifier = hash_password(self.__password, salt)

        self.tr.debug(f'[{self.name}]: Sending login request to {server}')
        return server.login(self.name, pwd_verifier)

    def logout_from(self, server: Server) -> bool:
        self.tr.debug(f'[{self.name}]: Sending logout request to {server}')
        return server.logout(self.name)

    def change_password_on(self, server: Server, new_password: str) -> bool:
        self.__password = new_password.encode()
        public_infos = self.__gen_public_infos() # Generate new public infos using new password (new salt as well)
        self.tr.debug(f'[{self.name}]: Request a passord update on {server}')
        return server.update_user_credentials(public_infos)

    def send_message(self, data: str, recipient_name: str, unlock_day: date, server: Server) -> bool:
        self.tr.debug(f'[{self.name}]: Getting {recipient_name} public key on {server}')
        recipient_pk = server.get_public_key(recipient_name)
        if not recipient_pk:
            self.tr.error(f'[{self.name}]: No public key associated to {recipient_name} on ({server})')
            return False

        # generate a public key to crypt the message
        self.tr.debug(f'[{self.name}]: Generating a public key')
        sym_key = gen_symmetric_key() 
        
        # Authenticated data : sender | recipient | date
        aad = AAD(sender=self.name, recipient=recipient_name, unlock_day=unlock_day)

        # encrypt message using AEAD 
        self.tr.debug(f'[{self.name}]: Encrypting message data')
        encrypted = encrypt_message(data.encode(), aad.encode(), sym_key)

        # TODO : Encrypt the AEAD encryption key using recipient public key
        self.tr.debug(f'[{self.name}]: Encrypting symmetric key')
        crypted_sym_key = encrypt_sym_key(sym_key, recipient_pk)

        # Pack message
        message = Message(encrypted, aad, crypted_sym_key)
        
        decrypted = decrypt_message(encrypted=message.data, aad=message.aad.encode(), key=message.key)
        self.tr.colorprint(decrypted.decode('utf-8'), 'yellow')

        self.tr.debug(f'[{self.name}]: Sending message on {server}')
        return server.store_message(message)

    def get_my_messages(self, server: Server) -> Message | None:
        self.tr.debug(f'[{self.name}]: Requesting messages metadata from {server}')
        return server.get_metadata(self.name)
    
    def read_message(self, server: Server, id: int) -> str | None:
        self.tr.debug(f'[{self.name}]: Requesting message {id} from {server}')
        message = server.get_message(id, self.name)
        if not message: 
            self.tr.error(f'[{self.name}]: Message with id: {id} does not exist')
            return None
        
        self.tr.debug(f'[{self.name}]: Decrypting message data')
        decrypted = decrypt_message(encrypted=message.data, aad=message.aad.encode(), key=message.key)
        if decrypted :
            return decrypted.decode('utf-8')

    def __str__(self):
        return f"{self.name}"