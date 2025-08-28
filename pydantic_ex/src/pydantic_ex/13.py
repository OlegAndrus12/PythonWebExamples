from pydantic import BaseModel, ConfigDict, Field, ValidationError


class Point2D(BaseModel):
    x: float = 0
    y: float = 0

class Circle2D(BaseModel):
    center: Point2D
    radius: float = Field(default=1, gt=0)


c = Circle2D(center=Point2D(x=1, y=1), radius=2)
print(c)
print(c.model_dump())
print(c.model_dump_json(indent=2))


from pydantic import BaseModel, Field, ConfigDict  # Pydantic v2

class User(BaseModel):
    model_config = ConfigDict(populate_by_name=True)  # Pydantic v2

    full_name: str = Field(alias="fullName")

# Now both work:
User(fullName="Alice")       # ✅ using alias
User(full_name="Alice")      # ✅ using field name


json_data = """
{
    "firstName": "David",
    "lastName": "Hilbert",
    "contactInfo": {
        "email": "d.hilbert@spectral-theory.com",
        "homePhone": {
            "countryCode": 49,
            "areaCode": 551,
            "localPhoneNumber": 123456789
        }
    },
    "personalInfo": {
        "nationality": "German",
        "born": {
            "date": "1862-01-23",
            "place": {
                "city": "Konigsberg",
                "country": "Prussia"
            }
        },
        "died": {
            "date": "1943-02-14",
            "place": {
                "city": "Gottingen",
                "country": "Germany"
            }
        }
    },
    "awards": ["Lobachevsky Prize", "Bolyai Prize", "ForMemRS"],
    "notableStudents": ["von Neumann", "Weyl", "Courant", "Zermelo"]
}
"""



# pip install "pydantic[email]"

from pydantic import EmailStr, PastDate
from pydantic.alias_generators import to_camel


class ContactInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: EmailStr | None = None

class PlaceInfo(BaseModel):
    city: str
    country: str
    
class PlaceDateInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    date_: PastDate = Field(alias="date")
    place: PlaceInfo
    
class PersonalInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    nationality: str
    born: PlaceDateInfo

class Person(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="ignore")
    
    first_name: str
    last_name: str
    contact_info: ContactInfo
    personal_info: PersonalInfo
    notable_students: list[str] = []


p = Person.model_validate_json(json_data)
print(p)
