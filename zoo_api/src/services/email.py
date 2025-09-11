from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pathlib import Path
from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME="debb5a8e45e0ea",
    MAIL_PASSWORD="a5339708014a52",
    MAIL_FROM="andrusoleg123@gmail.com",
    MAIL_PORT=2525,
    MAIL_SERVER="sandbox.smtp.mailtrap.io",
    MAIL_FROM_NAME="Cats and Owners App",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_email(email: str, username: str, host: str):
    token_verification = await auth_service.create_jwt_token({"email": email}, scope="verification_token")
    try:
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )
        smtp_server = FastMail(conf)
        await smtp_server.send_message(message, template_name="email_verification.html")
    except ConnectionErrors as err:
        print(err)
