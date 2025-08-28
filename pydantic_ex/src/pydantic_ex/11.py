from pydantic.alias_generators import to_camel, to_snake, to_pascal

var = "years_of_experience"

print(to_camel(var))
print(to_snake(var))
print(to_pascal(var))

from pydantic import BaseModel, ConfigDict

class Person(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)

    years_of_experience: int
    first_name: str | None = None
    last_name: str
    age: int | None = None


person = """
        {   
            "yearsOfExperience": 20, 
            "firstName": "Isaac",
            "lastName": "Newton",
            "age": 44
        }
        """
isaac = Person.model_validate_json(person)
print(isaac)
print(isaac.first_name)
print(Person.model_fields)
print(isaac.model_dump_json())
print(isaac.model_dump_json(by_alias=True))
