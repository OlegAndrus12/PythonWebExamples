from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas.users import UserRegisterSchema


async def get_user_by_email(email:str, db: Session):
    print(db.query(User).filter_by(email=email).all())
    return db.query(User).filter_by(email=email).first()

async def create_user(body: UserRegisterSchema, db: Session):
    user = User(**body.model_dump())
    db.add(user)
    db.commit()
    return user


async def change_confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()

