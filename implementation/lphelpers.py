# Tracing helpers
from colorama import Fore
import numpy as np
class tracer :
    def __init__(self, trace_level:str = 'DEBUG', default_color:str='WHITE'):
        self.levels = {'ERROR':1, 'WARNING':2, 'INFO':3, 'DEBUG':4}
        if trace_level not in self.levels:
            raise ValueError(f"Invalid trace level: {trace_level}")
        self.level = self.levels[trace_level]
        self.default_color = default_color

    @staticmethod     
    def colorstring(s:str, color:str='WHITE') -> str : 
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
        color_code = colors.get(color.upper(), Fore.WHITE)
        return color_code + s + Fore.RESET
    def colorprint(self, s:str, color:str='DEFAULT'):
        if color == 'DEFAULT' : color = self.default_color 
        print(self.colorstring(s, color))

    def error(self, s):
        if self.level >= self.levels['ERROR'] : self.colorprint('[ERROR]: ' + s, color='RED')
    def warn(self, s):
        if self.level >= self.levels['WARNING'] : self.colorprint('[WARNING]: ' + s, color='YELLOW')
    def info(self, s):
        if self.level >= self.levels['INFO'] : self.colorprint('[INFO]: ' + s, color='WHITE')
    def debug(self, s):
        if self.level >= self.levels['DEBUG'] : self.colorprint('[DEBUG]: ' + s, color='BLUE')

    def sepline(self, size:int, text:str = None, char:str='_', color:str='DEFAULT'):
        if text:
            side = max(size - len(text) - 2, 0)
            left = char * (side // 2)
            right = char * (side - len(left))
            self.colorprint(f'{left} {text} {right}', color)
        else:
            self.colorprint(char * size, color)
     
    def show_nparray(self, matrix:np.ndarray, name:str='Matrix', N:int=5, precision:int=4, color:str='DEFAULT'):
        info_str = f'Infos: shape = {matrix.shape} | dtype = {matrix.dtype}'

        Nel_str = None
        display_matrix = matrix

        # Truncate if too large
        if matrix.ndim == 1 and len(matrix) > N:
            Nel_str = f'({N} elements)'
            display_matrix = matrix[:N]
        elif matrix.ndim > 1 and matrix.shape[0] > N:
            Nel_str = f'({N} rows)'
            display_matrix = matrix[:N]

        with np.printoptions(precision=precision, suppress=True):
            matrix_str = str(display_matrix)

        # Compute max line length for clean separators
        sepline_len = max(len(info_str), max(map(len, matrix_str.splitlines())))

        self.sepline(sepline_len, text=name, color=color)
        self.colorprint(info_str, color=color)
        self.sepline(sepline_len, text=Nel_str, char='-', color=color)
        self.colorprint(matrix_str, color=color)
        self.sepline(sepline_len, color=color)

def print_header(text:str, color:str='WHITE', size:int=60):
    tr = tracer(default_color=color)
    print()
    tr.sepline(size=size, char='-')
    tr.sepline(size=size, text=text, char=' ')
    tr.sepline(size=size, char='-')

def colorprint(s:str, color:str='DEFAULT'):
    tracer().colorprint(s, color)

def sepline(size:int, text:str = None, char:str='_', color:str='DEFAULT'):
    tracer().sepline(size, text, char, color)