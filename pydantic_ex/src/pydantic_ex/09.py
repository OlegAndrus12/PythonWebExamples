# curl https://get.geojs.io/v1/ip/geo.json | jq
# curl https://get.geojs.io/v1/ip/geo/8.8.8.8.json | jq

import requests
from pydantic import BaseModel, ConfigDict, Field, field_validator, ValidationError, IPvAnyAddress


class IPGeo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ip_address: IPvAnyAddress = Field(alias="ip")
    country: str | None = None
    country_code: str | None = Field(default=None, min_length=2, max_length=2)
    country_code3: str | None = Field(default=None, min_length=2, max_length=3)
    city: str | None = None
    region: str | None = None
    timezone: str | None= None
    organization_name: str | None = None

    @field_validator("organization_name")
    def set_unknown_to_none(cls, value: str):
        if value.casefold() == "unknown":
            return None
        return value

url_query = "https://get.geojs.io/v1/geo/{ip_address}.json"
url = url_query.format(ip_address="8.8.8.8")
response = requests.get(url)
response.raise_for_status()
response_json= response.json()
print(response.json())
data = IPGeo.model_validate(response.json())
print(data)