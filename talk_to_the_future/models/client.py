from models.server import Server
from models.aad import AAD
from utils.logger import Tracer
from datetime import date
from crypto import generate_keys, encrypt_and_sign, decrypt_and_verify

class Client: 
    def __init__(self, name: str, password: str, tr:Tracer = Tracer(trace_level='DEBUG')):
        self.name:str = name
        self.server: Server = None
        
        self.__password:str = password # private attribute, contains plaintext password
        self.public_keys: dict[str, bytes] = None # contains salt, password_tag, public_key and verify_key
        self.__private_keys: dict[str, bytes] = None # private attribute, contains private_key and signing_key
        self.token: bytes = None

        self.tr:Tracer = tr     # Tracer to handle general verbosity of the User
                                # 4 possible levels: ERROR, WARNING, INFO, DEBUG

    
    def register_on(self, server: Server) -> bool:
        '''
        Generate new `public_keys` then use it to register on a `server`.
        
        Args:
            `server` (Server): The server to register on.
        
        Returns:
            bool: True if registration succeeded else false.
        '''
        self.server = server

        username = self.name
        
        self.tr.debug(f'[{self.name}]: Generating keys...')
        self.__private_keys, self.public_keys = generate_keys(self.__password)
        
        self.tr.debug(f'[{self.name}]: Request a registration on {server}')
        return server.register(username, self.public_keys)

    def login_on(self, server: Server) -> bool:
        '''
        Generate new `private_keys` and `public_keys` then uses public ones to login on a `server`.
        
        Args:
            `server` (Server): The server to login on.
        
        Returns:
            bool: True if login succeeded else false.
        '''
        self.server = server

        self.tr.debug(f'[{self.name}]: Getting salt from {self.server}')
        salt = self.server.get_user_salt(self.name)                                  
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
        '''
        Logout from the current `self.server`.

        Returns:
            bool: True if logout succeeded else false.
        '''
        self.tr.debug(f'[{self.name}]: Sending logout request to {self.server}')
        return self.server.logout(self.name, self.token)

    def change_password(self, new_password: str) -> bool:
        '''
        Generate new `private_keys` and `public_keys` based on a `new_password`.
        Call a key update on current `self.server`.

        Args:
            `new_password` (str): New password used to generate keys.
        
        Returns:
            bool: True if update succeeded else false.
        '''
        self.__password = new_password
        
        self.tr.debug(f'[{self.name}]: Generating keys...')
        self.__private_keys, self.public_keys = generate_keys(self.__password)
        
        self.tr.debug(f'[{self.name}]: Updating credentials on {self.server}')
        return self.server.update_keys(self.name, self.token, self.public_keys)

    def send_message(self, content: str, receiver_name: str, unlock_day: date) -> bool:
        '''
        Send a message to a given `receiver_name` through `self.server`

        Args:
            `content` (str): Content of the message.
            `receiver_name` (str): Name of the receiver of the message.
            `unlock_day` (str): Date at which receiver can read the message.
        
        Returns:
            bool: True if message was successfully saved in server else false.
        '''
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
        return self.server.send_message(self.name, self.token, message)

    def get_messages_aad(self) -> list[AAD] | None:
        '''
        Ask `self.server` for metadata about received messages.
        
        Returns:
            list[AAD]: An AAD object (From|To|Unlock_day) for each received message.
        '''
        self.tr.debug(f'[{self.name}]: Requesting message metadata from {self.server}')
        return self.server.get_messages_aad(self.name, self.token)
    
    def read_message(self, message_id: int) -> str | None:
        '''
        Ask `self.server` for message with a given `message_id`.
        Verify signature and decrypt content.

        Args:
            `message_id` (int): Desired message ID.
        
        Returns:
            str: Plaintext content of desired message.
        '''
        self.tr.debug(f'[{self.name}]: Requesting full message (id:{message_id}) from {self.server}')
        encoded_msg = self.server.get_message_payload(self.name, self.token, message_id, no_key=False)

        if not encoded_msg: 
            self.tr.error(f'[{self.name}]: Unable to read message (id:{message_id})')
            return None

        self.tr.debug(f'[{self.name}]: Decrypting message content')
        return decrypt_and_verify(payload=encoded_msg, receiver_private_key=self.__private_keys["private_key"]).decode('utf-8')
        
    def download_future_message(self, message_id: int) -> dict[str, bytes] | None:
        '''
        Ask `self.server` for message with a given `message_id` without the encryption key.

        Args:
            `message_id` (int): Desired message ID.
        
        Returns:
            dict[str, bytes]: Dictionary containing ciphertext, aad, signature, sender_verify_key
        '''
        self.tr.debug(f'[{self.name}]: Downloading future message (id:{message_id}) without key')
        return self.server.get_message_payload(self.name, self.token, message_id, no_key=True)
    
    def get_msg_enc_sym_key(self, message_id: int) -> bytes | None:
        '''
        Ask `self.server` for the encryption key of the message with a given `message_id`.

        Args:
            `message_id` (int): Desired message ID.
        
        Returns:
            bytes: `enc_sym_key` to decrypt message `message_id`
        '''
        self.tr.debug(f'[{self.name}]: Requesting key for message (id:{message_id})')
        enc_sym_key = self.server.get_message_key(self.name, self.token, message_id)

        if not enc_sym_key: 
            self.tr.error(f'[{self.name}]: Unable to get symmetric key for this message (id:{message_id})')
            return None
        return enc_sym_key

    def decrypt_message(self, message: dict[str, bytes]) -> str:
        '''
        Verify signature and decrypt a `message` without calling the server.

        Args:
            `message` (dict[str, bytes]): Message full payload with ciphertext, aad, signature, sender_verify_key, enc_sym_key
        
        Returns:
            str: Plaintext content of `message`.
        '''
        return decrypt_and_verify(payload=message, receiver_private_key=self.__private_keys["private_key"]).decode('utf-8')
    
    def delete_message(self, message_id: int) -> bool:
        '''
        Ask `self.server` to delete the message with a given `message_id`.

        Args:
            `message_id` (int): Desired message ID.
        
        Returns:
            bool: True if succeed, else False
        '''
       
        return self.server.delete_message(self.name, self.token, message_id)
    
    def __str__(self):
        return f"{self.name}"