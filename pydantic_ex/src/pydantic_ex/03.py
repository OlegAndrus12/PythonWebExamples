# type conversions
# lax / strict modes
# lax means trying to convert (by default)
# strict means only specified type even if conversion is possible

# conversion table https://docs.pydantic.dev/latest/concepts/conversion_table/#__tabbed_1_1

from pydantic import BaseModel, ValidationError

class Coordinates(BaseModel):
    x: float
    y: float

p1 = Coordinates(x=1.1, y=2.2)
print(p1)

print(Coordinates.model_fields)
print(type(p1.x))

p2 = Coordinates(x=0, y="1.2")
print(p2)
print(type(p1.x), type(p1.x))


from pydantic import BaseModel, ConfigDict

class Coordinates(BaseModel):
    model_config = ConfigDict(strict=True)

    x: float
    y: float

p2 = Coordinates(x=0, y="1.2")
print(p2)
print(type(p1.x), type(p1.x))

from pydantic import BaseModel, StrictStr, StrictInt

class User(BaseModel):
    name: StrictStr
    age: StrictInt

p2 = Coordinates(x=0, y="1.2")
print(p2)
print(type(p1.x), type(p1.x))