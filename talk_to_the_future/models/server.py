from models.user_infos import UserInfos
from utils.logger import Tracer

class Server: 
    def __init__(self, name:str='Server', tr:Tracer = Tracer(trace_level='DEBUG')):
        self.name:str = name
        self.users:list[UserInfos]  = []

        self.tr:Tracer = tr     # Tracer to handle general verbosity of the Server
                                # 4 possible levels : ERROR, WARNING, INFO, DEBUG

    def register(self, new_user: UserInfos) -> bool: 
        if all(user.name != new_user.name  for user in self.users):
            self.users.append(new_user)
            self.tr.info(f"[{self}]: New user {new_user.name} was added!")
            return True
        self.tr.error(f"[{self}]: User {new_user.name} already exists!")
        return False
    
    def remove(self, requester_name) -> None :
        self.users = [user for user in self.users if user.name != requester_name]
        self.tr.info(f"[{self}]: User {requester_name} was successfully removed!")

    def get_user_salt(self, requester_name: str) -> bytes | None :
        for user in self.users :
            if user.name == requester_name :
                return user.salt
        self.tr.error(f"[{self}]: No user is registered as : {requester_name}")
        return None
    
    def login(self, requester_name:str, requester_pwd_verifier:bytes) -> bool :
        for user in self.users :
            if user.name == requester_name :
                if user.pwd_verifier == requester_pwd_verifier :
                    user.isconnected = True
                    self.tr.info(f'[{self}]: User {requester_name} is now connected!')
                    return True
                else : 
                    self.tr.error(f'[{self}]: Wrong password!')
                    return False
        self.tr.error(f"[{self}]: No user is registered as : {requester_name}")
        return False
    
    def logout(self, requester_name) -> bool:
        for user in self.users:
            if user.name == requester_name:
                if not user.isconnected :
                    self.tr.warn(f'[{self}]: User {requester_name} is not logged in.')
                user.isconnected = False
                self.tr.info(f"[{self}]: {requester_name} has been logged out.")
                return True
        self.tr.error(f"[{self}]: No user is registered as: {requester_name}")
        return False

    def update_user_credentials(self, requester:UserInfos) -> bool :
        for user in self.users :
            if user.name == requester.name :
                if not user.isconnected :
                    self.tr.warn(f'[{self}]: Please login before!')
                    return False
                user.pwd_verifier = requester.pwd_verifier
                user.salt = requester.salt
                self.tr.info(f"[{self}]: Password updated for {user.name}.")
                return True
        self.tr.error(f"[{self}]: No user is registered as : {requester.name}.")
        return False

    def show_registered_users(self):
        for user in self.users :
            self.tr.info(user.name)

    def __str__(self):
        return f"{self.name}"