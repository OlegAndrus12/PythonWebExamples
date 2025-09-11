from pydantic import EmailStr, BaseModel


class OwnerSchema(BaseModel):
    email: EmailStr


