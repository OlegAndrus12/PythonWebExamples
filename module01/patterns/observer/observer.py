import datetime
from rich.console import Console
from enum import Enum

# https://refactoring.guru/uk/design-patterns/observer

console = Console()

class MessageStatus(Enum):
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"

class Event:
    _observers = []

    def register(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event, message):
        for observer in self._observers:
            observer(event, message)


def console_logger(status, message):
    
    match status:
        case MessageStatus.WARNING:
            style = "bold yellow"
        case MessageStatus.ERROR:
            style = "bold red"
        case _:
            style = "bold green"
    
    console.print(f"[{status}]: {message}", style=style)



class FileLogger:
    def __init__(self, filename):
        self.filename = filename

    def __call__(self, event, message):
        # why "a" option? what it does
        with open(self.filename, "a") as fl:
            fl.write(f"{datetime.datetime.now()}: [{event}] - {message}\n")


if __name__ == "__main__":
    event = Event()

    event.register(console_logger)
    fl = FileLogger("logs.txt")
    event.register(fl)
    # WRAP TO THE LOOP
    event.notify(MessageStatus.WARNING, "RSA128 is deprecated")
    event.notify(MessageStatus.ERROR, "File users.json does not exosts")
    event.notify("SUCCESS", "/user/login - 200")
    event.unregister(fl)
    event.unregister(console_logger)
    event.notify("WARNING", "/user/login - User email is not verified")