""" 
Automobile model that contains the following fields:

manufacturer, string, required, not nullable
series_name, string, required, not nullable
type_, string, required, not nullable
is_electric, boolean, defaults to False, not nullable
manufactured_date, date, required, not nullable
base_msrp_usd, float, required, not nullable
vin, string, required, not nullable
number_of_doors, integer, defaults to 4, not nullable
registration_country, string, defaults to None
license_plate, string, defaults to None


Once you have created your model, you should test deserializing 
and serializing your model and make sure everything works.

"""

from datetime import date

data = {
    "manufacturer": "BMW",
    "series_name": "M4",
    "type_": "Convertible",
    "is_electric": False,
    "manufactured_date": "2023-01-01",
    "base_msrp_usd": 93_300,
    "vin": "1234567890",
    "number_of_doors": 2,
    "registration_country": "France",
    "license_plate": "AAA-BBB",
}

data_expected_serialization = {
    'manufacturer': 'BMW',
    'series_name': 'M4',
    'type_': 'Convertible',
    'is_electric': False,
    'manufactured_date': date(2023,1,1),
    'base_msrp_usd': 93_300,
    'vin': '1234567890',
    'number_of_doors': 2,
    'registration_country': 'France',
    'license_plate': 'AAA-BBB',
}


# JSON
data_json = '''
{
    "manufacturer": "BMW",
    "series_name": "M4",
    "type_": "Convertible",
    "manufactured_date": "2023-01-01",
    "base_msrp_usd": 93300,
    "vin": "1234567890"
}
'''

data_json_expected_serialization = {
    'manufacturer': 'BMW',
    'series_name': 'M4',
    'type_': 'Convertible',
    'is_electric': False,
    'manufactured_date': date(2023, 1, 1),
    'base_msrp_usd': 93_300,
    'vin': '1234567890',
    'number_of_doors': 4,
    'registration_country': None,
    'license_plate': None,
}

from datetime import date
from pydantic import BaseModel


class Automobile(BaseModel):
    manufacturer: str
    series_name: str
    type_: str
    is_electric: bool = False
    manufactured_date: date
    base_msrp_usd: float
    vin: str
    number_of_doors: int = 4
    registration_country: str | None = None
    license_plate: str | None = None

car = Automobile.model_validate(data)
print(car)
assert car.model_dump() == data_expected_serialization

car = Automobile.model_validate_json(data_json)
print(car)

assert car.model_dump() == data_json_expected_serialization

