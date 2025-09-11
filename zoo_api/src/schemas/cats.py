
from pydantic import BaseModel, Field

class CatSchema(BaseModel):
    nickname: str = Field(min_length=4, max_length=16)
    age: int = Field(1, ge=0, le=12)
    vaccinated: bool = False
    description: str = ""
    owner_id: int = Field(gt=0)


class CatResponse(BaseModel):
    nickname: str
    age: int
    vaccinated: bool
    description: str 
