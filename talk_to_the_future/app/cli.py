from utils.logger import Tracer, print_header
from models import Client, Server
import questionary
import sys

class TalkToTheFutureCLI:
    def __init__(self, trace_level='DEBUG'):
        self.tracer = Tracer(trace_level=trace_level, default_color='LIGHTYELLOW_EX')
        self.server = Server(name='3TF - Server', tr=self.tracer)

    def run(self) -> None:
        self.tracer.colorprint("\nWelcome to TalkToTheFuture!")
        self.main_menu()

    def main_menu(self) -> None:
        while True:
            print_header(text='Main menu', color='LIGHTMAGENTA_EX')
            choice = questionary.select("Choose an option?", ["Register", "Login", "Exit"]).ask()
            match choice: 
                case "Register":
                    client = self.ask_credentials()
                    client.register_on(self.server)
                case "Login":
                    client = self.ask_credentials()
                    if client.login_on(self.server):
                        self.user_menu(client)
                case "Exit":
                    self.exit_app()
    
    def user_menu(self, client: Client) -> None:
        print_header(text=f'{client.name} - Menu', color='LIGHTGREEN_EX')
        choices  = [
            "Send a message",
            "Read my messages",
            "Change my password",
            "Logout",
            "Exit"
        ]
        choice = questionary.select("Choose an option?",choices).ask()
        match choice:
            case "Send a message":
                self.tracer.colorprint('TO DO', color='yellow')
            case "Read my messages":
                self.tracer.colorprint('TO DO', color='yellow')
            case "Change my password":
                client.change_password_on(self.server, self.ask_new_password())
            case "Logout":
                client.logout_from(self.server)
            case "Exit":
                self.exit_app()

    def ask_credentials(self) -> Client:
        username:str = questionary.text('Username:').ask()
        password:str = questionary.password('Password:').ask()
        return Client(username, password, self.tracer)
    
    def ask_new_password(self) -> str:
        return questionary.password('New password:').ask()
    
    def exit_app(self) -> None:
        self.tracer.colorprint("\nThank you for using TalkToTheFuture!\n")
        sys.exit()