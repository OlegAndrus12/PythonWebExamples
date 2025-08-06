"""
Dependency Injection (DI) is a way to provide dependencies
to a class rather than having the class create them itself.

Dependency Inversion (DPI):
High-level modules should not depend on low-level modules. 
Both should depend on abstractions.

Abstractions should not depend on details. Details should depend on abstractions.

"""


class EmailService:
    def send(self, email_address, message):
        print(f"Sending email to {email_address}: {message}")


class SMSService:
    def notify(self, phone_number, text):
        print(f"SMS is sent to {phone_number} with the text: {text}")


class UserService:
    def __init__(self, service):
        self.email_service = service

    def register_user(self, email: str):
        self.email_service.send(email, "Welcome!", "Thanks for registering.")


UserService(EmailService())
UserService(SMSService())