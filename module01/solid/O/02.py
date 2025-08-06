from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def send(self, message):
        pass

class EmailNotifier(Notifier):
    def send(self, message: str):
        print(f"Sending Email: {message}")


class SMSNotifier(Notifier):
    def send(self, message: str):
        print(f"Sending SMS: {message}")

class DesktopNotifier(Notifier):
    pass

class TelegramNotifier(DesktopNotifier):
    def send(self, message: str):
        print(f"Sending Telegram: {message}")

class SlackNotifier(DesktopNotifier):
    def send(self, message: str):
        print(f"Sending Slack message: {message}")

class NotificationService:
    def __init__(self, notifires: list):
        self.notifiers = notifires
    
    def notify_all(self, message):
        for notifier in self.notifiers:
            notifier.send(message)


service = NotificationService(
    [
        EmailNotifier(),
        EmailNotifier(),
    ]
)

service.notify_all("Black Friday is coming!")
service.notify_all("Black Friday is coming!")

