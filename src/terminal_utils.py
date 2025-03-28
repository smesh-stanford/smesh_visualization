import datetime
import pathlib

DATETIME_COLOR = '\033[92m' # Green
ISSUE_COLOR = '\033[91m' # Red
COLOR_START = '\033[96m' # Cyan
COLOR_END = '\033[0m'

def with_color(text: str, color: str = COLOR_START) -> str:
    return color + str(text) + COLOR_END

def print_issue(text: str, color: str = ISSUE_COLOR) -> None:
    print(color + text + COLOR_END)

def now_print(text: str, color: str = DATETIME_COLOR) -> None:
    print(color + "[" + str(datetime.datetime.now()) + "]" + COLOR_END, text)


def check_directory_cascade_exists(directory: pathlib.Path) -> None:
    """
    Check if a directory and its parents exist. Used as debugging tool to check
    where the directory is not being found.

    Args:
        directory (pathlib.Path): The directory to check.

    Returns:
        None
    """
    # The directory path may have many parents, so we need to check each one
    print("The current working directory is: ", pathlib.Path.cwd())

    if directory.is_dir():
        print("The directory exists: ", directory)
        return True
    else:
        print_issue("The directory does not exist: " + str(directory))
    
    for parent in directory.parents:
        if parent.is_dir():
            print("The parent directory exists: ", parent)
        else:
            print("The parent directory does not exist: ", parent)
    
    # Print the directories in the current working directory
    print("The directories in the current working directory are: ")
    for p in pathlib.Path.cwd().iterdir():
        if p.is_dir():
            print(p)

    return False
