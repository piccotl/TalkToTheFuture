from utils.logger import Tracer, print_header
from models import Client, Server
import questionary
import sys
from datetime import date, datetime

class TalkToTheFutureCLI:
    def __init__(self, trace_level='DEBUG'):
        self.tracer = Tracer(trace_level=trace_level, default_color='LIGHTYELLOW_EX')
        self.server = Server(name='Server', tr=self.tracer)

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
        print_header(text=f'{client.name} - Session Menu', color='LIGHTGREEN_EX')
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
                result = self.ask_message()
                if result :
                    content, receiver, unlock_date = result
                    client.send_message(content, receiver, unlock_date)
                self.user_menu(client)
            case "Read my messages":
                self.read_menu(client)
                self.user_menu(client)
            case "Change my password":
                client.change_password(self.ask_new_password())
            case "Logout":
                client.logout()
            case "Exit":
                self.exit_app()
    
    def read_menu(self, client: Client) -> None:
        print_header(text=f'{client.name} - Read Menu', color='LIGHTCYAN_EX')
        messages = client.get_my_messages()
        if not messages :
            self.tracer.colorprint("\nYou didn't receive any message!\n")
            return
        choices = [questionary.Choice(title=f"id {i}: {msg}", value=i) for i, msg in enumerate(messages)]
        selected_id = questionary.select("Choose the message you want to read",choices).ask()
        
        content = client.read_message(selected_id)
        if not content:
            self.tracer.colorprint("Your message could not be read")
            return None
        self.tracer.colorprint(f"\nMessage {selected_id} : {messages[selected_id]}")
        self.tracer.sepline(60)
        self.tracer.colorprint(content, color='YELLOW')


    def ask_credentials(self) -> Client:
        username:str = questionary.text('Username:').ask()
        password:str = questionary.password('Password:').ask()
        return Client(username, password, self.tracer)
    
    def ask_new_password(self) -> str:
        return questionary.password('New password:').ask()
    
    def ask_message(self) -> tuple[str, str, date] | None:
        receiver:str = questionary.text('To:').ask()
        content:str = questionary.text('Message:').ask()
        unlock_date_str:str = questionary.text("Unlock date (YYYY-MM-DD):", default="2002-05-29").ask()

        try:
            unlock_date:date = datetime.strptime(unlock_date_str, "%Y-%m-%d").date()
        except ValueError:
            self.tracer.error("Invalid date format. Please use YYYY-MM-DD.")
            return None
        return content, receiver, unlock_date
    
    def exit_app(self) -> None:
        self.tracer.colorprint("\nThank you for using TalkToTheFuture!\n")
        sys.exit()

