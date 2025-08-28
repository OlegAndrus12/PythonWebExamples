from pydantic import BaseModel


class Person(BaseModel):
    first_name: str
    last_name: str
    age: int

p = Person(first_name="Evariste", last_name="Galois", age=20)

# __str__ and __repr__ implemented by default
print(p)

print(Person.model_fields)

from pydantic import ValidationError
try:
    Person(last_name='Galois')
except ValidationError as ex:
    print(ex)

#Pydantic reports back on ALL the validation errors 
# it encounters. Not just the first one

# it's a regular class, you may add properties/methods
class Person(BaseModel):
    first_name: str
    last_name: str
    age: int

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name[0]}"

try:
    Person(first_name='Evariste', last_name='Galois', age='twenty')
except ValidationError as ex:
    print(ex)

p = Person(first_name="Evariste", last_name="Galois", age=20)
print(p.display_name)
p.age = 21
print(p)


p.age = "twenty"
print(p)

#Pydantic will perform validation when it loads data 
# (deserializes data) to create a model instance.