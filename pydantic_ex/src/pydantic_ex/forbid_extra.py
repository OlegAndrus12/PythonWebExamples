from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(extra="forbid")  # forbid extra fields
    id: int
    name: str

# Example usage
try:
    user = User(id=1, name="Alice", age=30)  # age is extra -> error
except Exception as e:
    print(e)

