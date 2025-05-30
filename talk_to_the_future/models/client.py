from models.user_infos import UserInfos
from models.server import Server
from utils.logger import Tracer
from crypto.kdf import hash_password, generate_salt

class Client: 
    def __init__(self, name : str, password : str, tr:Tracer = Tracer(trace_level='DEBUG')):
        self.name:str = name
        self.password:bytes = password.encode()
        self.tr:Tracer = tr     # Tracer to handle general verbosity of the User
                                # 4 possible levels : ERROR, WARNING, INFO, DEBUG
    
    def gen_public_infos(self) -> UserInfos:

        self.tr.debug(f'[{self.name}]: Drawing a random salt...')
        salt = generate_salt()

        self.tr.debug(f'[{self.name}]: Hashing password...')
        pwd_verifier = hash_password(self.password, salt)

        return UserInfos(self.name, pwd_verifier, salt)
    
    def register_on(self, server : Server) -> bool:
        public_infos = self.gen_public_infos()
        self.tr.debug(f'[{self.name}]: Request a registration on {server}')
        return server.register(public_infos)

    def login_on(self, server : Server) -> bool:

        self.tr.debug(f'[{self.name}]: Getting salt from {server}')
        salt = server.get_user_salt(self.name)                                  
        if (not salt) : return False

        self.tr.debug(f'[{self.name}]: Recomputing pwd_verifier')
        pwd_verifier = hash_password(self.password, salt)

        self.tr.debug(f'[{self.name}]: Sending login request to {server}')
        return server.login(self.name, pwd_verifier)

    def logout_from(self, server : Server) -> bool:
        self.tr.debug(f'[{self.name}]: Sending logout request to {server}')
        return server.logout(self.name)

    def change_password_on(self, server : Server, new_password : str) -> bool:
        self.password = new_password.encode()
        public_infos = self.gen_public_infos() # Generate new public infos using new password (new salt as well)
        self.tr.debug(f'[{self.name}]: Request a passord update on {server}')
        return server.update_user_credentials(public_infos)

    def __str__(self):
        return f"{self.name}"
