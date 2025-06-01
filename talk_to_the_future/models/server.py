from models.user_infos import UserInfos
from models.message import AAD, Message
from utils.logger import Tracer
from datetime import date

class Server: 
    def __init__(self, name:str='Server', tr:Tracer = Tracer(trace_level='DEBUG')):
        self.name:str = name
        self.__users:list[UserInfos]  = []
        self.tr:Tracer = tr     # Tracer to handle general verbosity of the Server
                                # 4 possible levels : ERROR, WARNING, INFO, DEBUG

    # Private Methods ---------------------------------------------------------------------
    def __get_user_by_name(self, name: str, check_login: bool = False) -> UserInfos | None:
        for user in self.__users:
            if user.name == name:
                if check_login and not user.isconnected: 
                    self.tr.warn(f'[{self}]: User {name} is not logged in.')
                    return None
                return user
        self.tr.error(f"[{self}]: No user is registered as : {name}")
        return None
    
    # Public methods -----------------------------------------------------------------------
    def register(self, new_user: UserInfos) -> bool: 
        if all(user.name != new_user.name  for user in self.__users):
            self.__users.append(new_user)
            self.tr.info(f"[{self}]: New user {new_user.name} was added!")
            return True
        self.tr.error(f"[{self}]: User {new_user.name} already exists!")
        return False
    
    def remove(self, requester_name) -> None :
        user = self.__get_user_by_name(requester_name)
        if user :
            self.__users.remove(user)
            self.tr.info(f"[{self}]: User {requester_name} was successfully removed!")
            return True
        return False

    def get_user_salt(self, requester_name: str) -> bytes | None :
        user = self.__get_user_by_name(requester_name)
        if not user :
            return None
        return user.salt
    
    def login(self, requester_name:str, requester_pwd_verifier:bytes) -> bool :
        user = self.__get_user_by_name(requester_name)
        if not user :
            return False
        if user.pwd_verifier == requester_pwd_verifier :
            user.isconnected = True
            self.tr.info(f'[{self}]: User {requester_name} is now connected!')
            return True
        else : 
            self.tr.error(f'[{self}]: Wrong password!')
            return False
    
    def logout(self, requester_name) -> bool:
        user = self.__get_user_by_name(requester_name, check_login=True)
        if not user :
            return False
        user.isconnected = False
        self.tr.info(f"[{self}]: {requester_name} has been logged out.")
        return True

    def update_user_credentials(self, requester: UserInfos) -> bool :
        user = self.__get_user_by_name(requester.name, check_login=True)
        if not user :
            return False
        user.pwd_verifier = requester.pwd_verifier
        user.salt = requester.salt
        self.tr.info(f"[{self}]: Password updated for {user.name}.")
        return True
        
    def show_registered_users(self):
        for user in self.__users:
            self.tr.info(user.name)
    
    def get_public_key(self, requested_name:str) -> bool | None:
        user = self.__get_user_by_name(requested_name)
        if not user :
            return None
        # return user.public_key
        return True # return true for now later return user's public_key
    
    def store_message(self, message: Message)-> bool:
        # check sender from authenticated data
        sender = self.__get_user_by_name(message.aad.sender, check_login=True)
        if not sender:
            return False
        
        # get and check recipient from authenticated data
        recipient = self.__get_user_by_name(message.aad.recipient)
        if not recipient:
            return False
        recipient.received_messages.append(message)
        
        self.tr.info(f"[{self}]: Message sent to {recipient.name}.")               
        return True
    
    def get_metadata(self, name: str) -> list[AAD] | None:
        user = self.__get_user_by_name(name, check_login=True)
        if not user:
            return None
        return [msg.aad for msg in user.received_messages]
    
    def get_message(self, message_id: int, username: str, no_key: bool = False) -> Message | None:
        user = self.__get_user_by_name(username, check_login=True)
        if not user:
            return None
        
        if not (0 <= message_id < len(user.received_messages)):
            self.tr.error(f"[{self}]: Message (id:{message_id}) does not exist for user {username}")
            return None

        message = user.received_messages[message_id]

        if date.today() < message.aad.unlock_day:
            if no_key:
                self.tr.info(f"[{self}]: Returning future message (id:{message_id}) without key")
                return Message(data=message.data, aad=message.aad, key=None)
            else:
                self.tr.warn(f"[{self}]: Access to message (id:{message_id}) is restricted until {message.aad.unlock_day}")
                return None
            
        self.tr.info(f"[{self}]: Returning message (id:{message_id}) with key")
        return message
    
    def get_message_key(self, message_id:int , username: str) -> bytes | None:
        user = self.__get_user_by_name(username, check_login=True)
        if not user:
            return None
        
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