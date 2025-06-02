from models.user_infos import UserInfos
from models.message import AAD, Message
from utils.logger import Tracer
from datetime import date
from crypto.token import gen_token

class Server: 
    def __init__(self, name:str='Server', tr:Tracer = Tracer(trace_level='DEBUG')):
        self.name:str = name
        self.__users:list[UserInfos]  = []
        self.__sessions:dict[str, str] = {} # (username: token)
        self.tr:Tracer = tr     # Tracer to handle general verbosity of the Server
                                # 4 possible levels : ERROR, WARNING, INFO, DEBUG

    # Private Methods ---------------------------------------------------------------------
    def __get_user(self, username: str) -> UserInfos | None:
        for user in self.__users:
            if user.name == username:
                return user
        self.tr.error(f"[{self}]: No user is registered as : {username}")
        return None
    
    def __check_session(self, username : str, token: str) -> bool:
        session = self.__sessions.get(username)
        if not session:
            self.tr.error(f'[{self}]: No active session found for {username}')
            return False
        if session != token:
            self.tr.error(f'[{self}]: Invalid token for {username}')
            return False
        return True

    # Public methods -----------------------------------------------------------------------
    def register(self, username:str, pwd_verifier: bytes, salt: bytes) -> bool: 
        if all(user.name != username  for user in self.__users):
            self.__users.append(UserInfos(username, pwd_verifier, salt))
            self.tr.info(f"[{self}]: New user {username} was added!")
            return True
        self.tr.error(f"[{self}]: User {username} already exists!")
        return False
    
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
        return user.salt
    
    def login(self, username:str, pwd_verifier:bytes) -> str | None :
        user = self.__get_user(username)
        if not user :
            return None
        if user.pwd_verifier != pwd_verifier :
            self.tr.error(f'[{self}]: Wrong password!')
            return None
        token: str = gen_token()
        self.__sessions[username] = token
        self.tr.info(f'[{self}]: User {username} is now connected!')
        return token
    
    def logout(self, username: str, token: str) -> bool:
        if not self.__check_session(username, token):
            return False
        del self.__sessions[username]
        self.tr.info(f"[{self}]: {username} has been logged out.")
        return True

    def update_user_credentials(self, username:str, token: str, new_pwd_verifier: bytes, new_salt: bytes) -> bool :
        if not self.__check_session(username, token):
            self.tr.warn(f"[{self}]: {username} must be logged in to update credentials")
            return False
        user: UserInfos = self.__get_user(username)
        user.pwd_verifier = new_pwd_verifier
        user.salt = new_salt
        self.tr.info(f"[{self}]: Password updated for {username}.")
        return True
        
    def show_registered_users(self):
        for user in self.__users:
            self.tr.info(user.name)
    
    def get_public_key(self, receiver:str) -> bool | None:
        user = self.__get_user(receiver)
        if not user :
            return None
        # return user.public_key
        return True # return true for now later return user's public_key
    
    def store_message(self, sender: str, token: str, message: Message)-> bool:
        if not self.__check_session(sender, token):
            return False
        
        # check sender from authenticated data
        if sender != message.aad.sender :
            self.tr.error(f"[{self}]: The session holder must be the sender of the message")
            return False
        
        # get and check receiver from authenticated data
        receiver = self.__get_user(message.aad.receiver)
        if not receiver:
            return False
        receiver.received_messages.append(message)
        
        self.tr.info(f"[{self}]: Message sent to {receiver.name}.")               
        return True
    
    def get_metadata(self, username: str, token: str) -> list[AAD] | None:
        if not self.__check_session(username, token):
            return None        
        user = self.__get_user(username)
        self.tr.debug(f"[{self}]: Returning {username}'s messages")
        return [msg.aad for msg in user.received_messages]
    
    def get_message(self, username: str, token: str, message_id: int, no_key: bool = False) -> Message | None:
        if not self.__check_session(username, token):
            return None        
        user: UserInfos = self.__get_user(username)
        
        if not (0 <= message_id < len(user.received_messages)):
            self.tr.error(f"[{self}]: Message (id:{message_id}) does not exist for user {username}")
            return None

        message = user.received_messages[message_id]

        if date.today() < message.aad.unlock_day:
            if no_key:
                self.tr.debug(f"[{self}]: Returning future message (id:{message_id}) without key")
                return Message(data=message.data, aad=message.aad, key=None)
            else:
                self.tr.warn(f"[{self}]: Access to message (id:{message_id}) is restricted until {message.aad.unlock_day}")
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
        
        message:Message = user.received_messages[message_id]

        if date.today() < message.aad.unlock_day:
            self.tr.warn(f"[{self}]: Key for message (id:{message_id}) not available until {message.aad.unlock_day}")
            return None
        
        return message.key
        
    def __str__(self):
        return f"{self.name}"