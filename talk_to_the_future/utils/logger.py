from colorama import Fore

class Tracer:
    def __init__(self, trace_level: str = 'DEBUG', default_color: str = 'WHITE'):
        self.levels = {'ERROR': 1, 'WARNING': 2, 'INFO': 3, 'DEBUG': 4}
        if trace_level not in self.levels:
            raise ValueError(f"Invalid trace level: {trace_level}")
        self.level = self.levels[trace_level]
        self.default_color = default_color

    @staticmethod     
    def colorstring(s: str, color: str = 'WHITE') -> str: 
        colors = {
            'BLACK': Fore.BLACK,
            'RED': Fore.RED,
            'GREEN': Fore.GREEN,
            'YELLOW': Fore.YELLOW,
            'BLUE': Fore.BLUE,
            'MAGENTA': Fore.MAGENTA,
            'CYAN': Fore.CYAN,
            'WHITE': Fore.WHITE,
            'RESET': Fore.RESET,
            'LIGHTBLACK_EX': Fore.LIGHTBLACK_EX,
            'LIGHTRED_EX': Fore.LIGHTRED_EX,
            'LIGHTGREEN_EX': Fore.LIGHTGREEN_EX,
            'LIGHTYELLOW_EX': Fore.LIGHTYELLOW_EX,
            'LIGHTBLUE_EX': Fore.LIGHTBLUE_EX,
            'LIGHTMAGENTA_EX': Fore.LIGHTMAGENTA_EX,
            'LIGHTCYAN_EX': Fore.LIGHTCYAN_EX,
            'LIGHTWHITE_EX': Fore.LIGHTWHITE_EX
        }
        return colors.get(color.upper(), Fore.WHITE) + s + Fore.RESET
    
    def colorprint(self, s: str, color: str = 'DEFAULT') -> None:
        color = self.default_color if color == 'DEFAULT' else color
        print(self.colorstring(s, color))

    def error(self, s) -> None:
        if self.level >= self.levels['ERROR'] : self.colorprint('[ERROR]: ' + s, color='RED')
    def warn(self, s) -> None:
        if self.level >= self.levels['WARNING'] : self.colorprint('[WARNING]: ' + s, color='YELLOW')
    def info(self, s) -> None:
        if self.level >= self.levels['INFO'] : self.colorprint('[INFO]: ' + s, color='WHITE')
    def debug(self, s) -> None:
        if self.level >= self.levels['DEBUG'] : self.colorprint('[DEBUG]: ' + s, color='BLUE')

    def sepline(self, size:int, text:str = None, char:str='_', color:str='DEFAULT'):
        if text:
            side = max(size - len(text) - 2, 0)
            left = char * (side // 2)
            right = char * (side - len(left))
            self.colorprint(f'{left} {text} {right}', color)
        else:
            self.colorprint(char * size, color)
     
# -- Global helper functions for logging --
def print_header(text: str, color: str = 'WHITE', size: int = 60) -> None:
    tr = Tracer(default_color=color)
    print()
    tr.sepline(size=size, char='-')
    tr.sepline(size=size, text=text, char=' ')
    tr.sepline(size=size, char='-')

def colorprint(s: str, color: str = 'DEFAULT') -> None:
    Tracer().colorprint(s, color)

def sepline(size: int, text: str | None = None, char:str='_', color:str='DEFAULT') -> None:
    Tracer().sepline(size, text, char, color)