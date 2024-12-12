import datetime

DATETIME_COLOR = '\033[92m' # Green
COLOR_START = '\033[96m' # Cyan
COLOR_END = '\033[0m'

def with_color(text: str, color: str = COLOR_START) -> str:
    return color + str(text) + COLOR_END

def now_print(text: str, color: str = DATETIME_COLOR) -> None:
    print(color + "[" + str(datetime.datetime.now()) + "]" + COLOR_END, text)
