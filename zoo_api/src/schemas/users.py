from pydantic import BaseModel, EmailStr


class UserRegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponseSchema(BaseModel):
    username: str
    email: EmailStr

class RequestEmail(BaseModel):
    email: EmailStr