from termcolor import colored,cprint

def info(message):
    COLOR = "blue"
    start = colored(f'(INFO)\t', COLOR, attrs=['bold'])
    msg = colored(f'{message}', COLOR)
    print(start + ' ' + msg)

def success(message):
    COLOR = "green"
    start = colored(f'(OK)\t', COLOR, attrs=['bold'])
    msg = colored(f'{message}', COLOR)
    print(start + ' ' + msg)

def error(message):
    COLOR = "red"
    start = colored(f'(ERROR)\t', COLOR, attrs=['bold'])
    msg = colored(f'{message}', COLOR)
    print(start + ' ' + msg)