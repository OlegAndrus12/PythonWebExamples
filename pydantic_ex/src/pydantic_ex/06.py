from pydantic import BaseModel

class Circle(BaseModel):
    center_x: int = 0
    center_y: int = 0
    radius: int = 1
    name: str | None = None

c1 = Circle(radius=2)
print(c1)

print(c1.model_dump())
print(Circle.model_fields)

# which fields were populated from data
print(c1.model_fields_set)


# which fields were populated from defaults
print(Circle.model_fields.keys() - c1.model_fields_set)


# what actually user send ?
print(c1.model_dump(include=c1.model_fields_set))