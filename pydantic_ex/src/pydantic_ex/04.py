

from pydantic import BaseModel


def send_request(url, timeout=None):
    # url is required param
    # timeout is optional param
    pass

class Circle(BaseModel):
    center: tuple[int, int] = (0, 0) # optional
    radius: int # required field

print(Circle.model_fields)


from datetime import datetime


# these values are calculated and stored with the function itself - 
# they are not re-created every time the function is called
# be careful specifying mutable objects by default
def log_time(history: list = []):
    history.append(datetime.now())
    return history

res = log_time()
print(res)

another_call = log_time()
print(another_call)

class User(BaseModel):
    hobby:list = []

u = User(hobby=["tenis"])
u.hobby.append("football")
print(u.hobby)

u2 = User(hobby=["softball"])
u2.hobby.append("hiking")
print(u2.hobby)