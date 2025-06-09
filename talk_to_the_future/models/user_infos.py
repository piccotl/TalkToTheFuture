class UserInfos :
    def __init__(self, name:str, keys:dict[str, bytes]):
        self.name = name
        self.keys: dict[str, bytes] = keys
        self.received_messages: list[dict[str, bytes]] = []

    def __str__(self):
        return f"{self.name}"