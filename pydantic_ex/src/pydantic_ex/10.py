from pydantic import BaseModel, Field, ValidationError

class Person(BaseModel):
    id_: int = Field(alias="id")
    first_name: str | None = Field(alias="firstName", default=None)
    last_name: str = Field(alias="lastName")
    age: int | None = None

isaac = Person(id=1, firstName="Isaac", lastName="Newton", age=84)
print(isaac)

print(isaac.model_dump())
print(isaac.model_dump(by_alias=True))
print(isaac.model_dump_json())
print(isaac.model_dump_json(by_alias=True))