class UserInfos :
    def __init__(self, name:str, pwd_verifier:bytes, salt:bytes):
        self.name = name
        self.pwd_verifier = pwd_verifier
        self.salt = salt
        self.isconnected:bool = False

    def __str__(self):
        return f"{self.name}"