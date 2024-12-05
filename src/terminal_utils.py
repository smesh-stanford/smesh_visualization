COLOR_START = '\033[96m'
COLOR_END = '\033[0m'

def with_color(text: str, color: str = COLOR_START) -> str:
    return color + str(text) + COLOR_END
