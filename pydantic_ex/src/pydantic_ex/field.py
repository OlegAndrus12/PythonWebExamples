from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List

class User(BaseModel):
    id: int = Field(description="Unique user ID", gt=0)
    name: str = Field(min_length=2, max_length=50, example="Alice")
    email: EmailStr = Field(title="User Email", example="alice@example.com")
    age: int = Field(default=18, ge=10, le=90, description="User age, must be between 10 and 90")
    tags: List[str] = Field(default_factory=list, description="Optional tags for the user")
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation datetime")

user = User(id=1, name="Bob", email="bob@example.com")
print(user.model_dump())
