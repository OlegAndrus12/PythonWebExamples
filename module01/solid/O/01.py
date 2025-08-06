
from enum import Enum

class ServiceType(Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"

class Notifier:
    # violate OCP
    def send(self, message, service=ServiceType.EMAIL):
        match service:
            case ServiceType.EMAIL:
                print(f"Sending Email: {message}")
            case ServiceType.SMS:
                print(f"Sending SMS: {message}")
            case ServiceType.SLACK:
                print(f"Sending Slack: {message}")

message = "Black Friday is coming"

notifier = Notifier()
notifier.send(message, ServiceType.SLACK)
notifier.send(message, ServiceType.EMAIL)