

from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int

try:
    User(id=None)
except ValidationError as ex:
    print(ex)

try:
    User()
except ValidationError as ex:
    print(ex)


class User(BaseModel):
    id: int | None

user = User(id=None)
print(user)

try:
    user = User()
    print(user)
except:
    pass

class User(BaseModel):
    id: int | None = None # type | type available since Python 3.10

from typing import Union

class User(BaseModel):
    id: Union[int | None] = None # type | type available since Python 3.10

user = User()

from typing import Optional

#Optional to indicate that field is nullable, 
# not to indicate that it is optional.

class User(BaseModel):
    id: Optional[int | None] # type | type available since Python 3.10

user = User()


#Required, Not Nullable
class User(BaseModel):
    id: int

#Required, Nullable
class User(BaseModel):
    id: int | None

#Optional, Not Nullable
class User(BaseModel):
    id: int = 0

# Optional, Nullable
class User(BaseModel):
    id: int | None = None