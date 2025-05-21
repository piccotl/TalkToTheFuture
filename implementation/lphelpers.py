# Tracing helpers
from colorama import Fore
class tracer :
    def __init__(self, trace_level:str):
        self.levels = {'ERROR':1, 'WARNING':2, 'INFO':3, 'DEBUG':4}
        self.trace_level = self.levels[trace_level]
    def error(self, s):
        if self.trace_level >= self.levels['ERROR'] : print(Fore.RED + s + Fore.RESET)
    def warn(self, s):
        if self.trace_level >= self.levels['WARNING'] : print(Fore.YELLOW + s + Fore.RESET)
    def info(self, s):
        if self.trace_level >= self.levels['INFO'] : print(Fore.WHITE + s + Fore.RESET)
    def debug(self, s):
        if self.trace_level >= self.levels['DEBUG'] : print(Fore.BLUE + s + Fore.RESET)
    def sepline(self, size, text=None, char='_', color=Fore.WHITE):
        if text:
            side = (size - len(text) - 2)
            left = char * (side // 2)
            right = char * (side - len(left))
            print(color + f'{left} {text} {right}' + Fore.RESET)
        else:
            print(color + char * size + Fore.RESET)

