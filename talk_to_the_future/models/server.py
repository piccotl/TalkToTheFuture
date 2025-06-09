from models.user_infos import UserInfos
from models.aad import AAD
from utils.logger import Tracer
from datetime import date
from crypto import generate_token

class Server: 
    def __init__(self, name:str='Server', tr:Tracer = Tracer(trace_level='DEBUG')):
        self.name:str = name
        self.__users:list[UserInfos]  = []
        self.__sessions:dict[str, str] = {} # (username: token)
        self.tr:Tracer = tr     # Tracer to handle general verbosity of the Server
                                # 4 possible levels : ERROR, WARNING, INFO, DEBUG

    # Private Methods ---------------------------------------------------------------------
    def __get_user(self, username: str) -> UserInfos | None:
        '''
        Find `username` in self.__users list.
        
        Args:
            `username` (str) : Desired user username.

        Returns: 
            UserInfos: Object containing informations on user (name, keys, received_messages)
        '''
        for user in self.__users:
            if user.name == username:
                return user
        self.tr.error(f"[{self}]: No user is registered as : {username}")
        return None
    
    def __check_session(self, username : str, token: str) -> bool:
        '''
        Check if a given username has an active session.
        
        Args: 
            `username` (str) : Name of the user.
            `token` (str) : Token of the active session to be checked.
        
        Returns: 
            bool : True if user is part of the connected users and the token is accurate, else False.
        '''
        session = self.__sessions.get(username)
        if not session:
            self.tr.error(f'[{self}]: No active session found for {username}')
            return False
        if session != token:
            self.tr.error(f'[{self}]: Invalid token for {username}')
            return False
        return True

    # Public methods -----------------------------------------------------------------------
    def register(self, username: str, keys: dict[str, bytes]) -> bool:

        # Check if user already exists
        if not all(user.name != username  for user in self.__users):
            self.tr.error(f"[{self}]: User {username} already exists!")
            return False

        # Check if all expected public keys are provided 
        if not {"salt", "password_tag", "public_key", "verify_key"} <= keys.keys():
            self.tr.error(f"[{self}]: User {username} needs to provide every key to register!")
            return False
        
        # Add user
        self.__users.append(UserInfos(username, keys))
        self.tr.info(f"[{self}]: New user {username} was added!")
        return True
        
    
    def remove(self, username: str, token: str) -> bool :
        if not self.__check_session(username, token):
            return False
        user = self.__get_user(username)
        self.logout(username, token)
        self.__users.remove(user)
        self.tr.info(f"[{self}]: User {username} was successfully removed!")
        return True

    def get_user_salt(self, username: str) -> bytes | None :
        user = self.__get_user(username)
        if not user:
            return None
        return user.keys["salt"]
    
    def login(self, username:str, pwd_verifier:bytes) -> str | None :
        user = self.__get_user(username)
        if not user :
            return None
        if user.keys["password_tag"] != pwd_verifier :
            self.tr.error(f'[{self}]: Wrong password!')
            return None
        token: str = generate_token()
        self.__sessions[username] = token
        self.tr.info(f'[{self}]: User {username} is now connected!')
        return token
    
    def logout(self, username: str, token: str) -> bool:
        if not self.__check_session(username, token):
            return False
        del self.__sessions[username]
        self.tr.info(f"[{self}]: {username} has been logged out.")
        return True

    def update_keys(self, username:str, token: str, new_keys: dict[str, bytes]) -> bool :
        # Check user session
        if not self.__check_session(username, token):
            self.tr.warn(f"[{self}]: {username} must be logged in to update his keys")
            return False
        user = self.__get_user(username)

        # Check if all expected public keys are provided 
        if not {"salt", "password_tag", "public_key", "verify_key"} <= new_keys.keys():
            self.tr.error(f"[{self}]: User {username} needs to provide every key to update his keys!")
            return False
        
        # Delete all messages as client won't have the key to read them anymore
        user.received_messages.clear() 

        # Update keys
        user.keys = new_keys
        self.tr.info(f"[{self}]: Keys updated for {username}.")
        return True
        
    def show_registered_users(self):
        for user in self.__users:
            self.tr.info(user.name)
    
    def get_public_key(self, receiver: str) -> bytes | None:
        user = self.__get_user(receiver)
        if not user :
            return None
        return user.keys["public_key"]
    
    def send_message(self, sender: str, token: str, message: dict[str, bytes])-> bool:
        # Check sender existancy and session
        sender_infos = self.__get_user(sender)
        if not sender_infos :
            return False
        if not self.__check_session(sender, token):
            return False
        
        # Get Authenticated data
        aad = AAD.decode(message["aad"])

        # check sender from authenticated data
        if sender_infos.name != aad.sender :
            self.tr.error(f"[{self}]: The session holder must be the sender of the message")
            return False
        
        # get and check receiver from authenticated data
        receiver = self.__get_user(aad.receiver)
        if not receiver:
            return False
        
        # Add sender's verify_key so receiver can check the signature
        message["verify_key"] = sender_infos.keys["verify_key"] 
        receiver.received_messages.append(message)
        
        self.tr.info(f"[{self}]: Message sent to {receiver.name}.")         
        return True
    
    def get_messages_aad(self, username: str, token: str) -> list[AAD] | None:
        if not self.__check_session(username, token):
            return None        
        user = self.__get_user(username)
        self.tr.debug(f"[{self}]: Returning {username}'s messages")
        return [AAD.decode(msg["aad"]) for msg in user.received_messages]
    
    def get_message_payload(self, username: str, token: str, message_id: int, no_key: bool = False) -> dict[str, bytes] | None:
        if not self.__check_session(username, token):
            return None        
        user: UserInfos = self.__get_user(username)
        
        if not (0 <= message_id < len(user.received_messages)):
            self.tr.error(f"[{self}]: Message (id:{message_id}) does not exist for user {username}")
            return None

        message = user.received_messages[message_id].copy()
        unlock_day = AAD.decode(message["aad"]).unlock_day

        if date.today() < unlock_day:
            if no_key:
                self.tr.debug(f"[{self}]: Returning future message (id:{message_id}) without key")
                del message["enc_sym_key"]
                return message
            else:
                self.tr.warn(f"[{self}]: Access to message (id:{message_id}) is restricted until {unlock_day}")
                return None
            
        self.tr.debug(f"[{self}]: Returning message (id:{message_id}) with key")
        return message
    
    def get_message_key(self, username: str, token: str, message_id:int) -> bytes | None:
        if not self.__check_session(username, token):
            return None        
        user: UserInfos = self.__get_user(username)
        
        if not (0 <= message_id < len(user.received_messages)):
            self.tr.error(f"[{self}]: Message (id:{message_id}) does not exist for user {username}")
            return None
        
        message = user.received_messages[message_id].copy()
        unlock_day = AAD.decode(message["aad"]).unlock_day

        if date.today() < unlock_day:
            self.tr.warn(f"[{self}]: Key for message (id:{message_id}) not available until {unlock_day}")
            return None
        
        return message["enc_sym_key"]
    
    def delete_message(self, username: str, token: str, message_id:int) -> bool:
        if not self.__check_session(username, token):
            return False        
        user: UserInfos = self.__get_user(username)
        
        if not (0 <= message_id < len(user.received_messages)):
            self.tr.error(f"[{self}]: Message (id:{message_id}) does not exist for user {username}")
            return False
        
        user.received_messages.pop(message_id)
        return True
        
    def __str__(self):
        return f"{self.name}"