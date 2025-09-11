
from sqlalchemy.orm import Session
from src.database.models import Cat


async def get_cats(db: Session):
    return db.query(Cat).all()

async def create_cat(body, db: Session):
    cat = Cat(**body.model_dump())
    db.add(cat)
    db.commit()
    return cat

async def get_cat_by_id(id, db: Session):
    return db.query(Cat).filter_by(id=id).first()
