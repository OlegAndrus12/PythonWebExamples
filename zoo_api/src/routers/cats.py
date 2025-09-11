from fastapi import Depends, APIRouter, HTTPException, status
from src.repository import cats as cats_repository
from src.schemas.cats import CatSchema, CatResponse
from src.database.db import get_db
from src.services.auth import auth_service

router = APIRouter(prefix="/cats", tags=['cats'], dependencies=[Depends(auth_service.get_current_user)])

@router.get("/")
async def get_cats_list(db = Depends(get_db)):
    cats = await cats_repository.get_cats(db)
    return cats

@router.get("/{cat_id}", response_model=CatResponse)
async def get_cat(cat_id:int, db = Depends(get_db)):
    cat = await cats_repository.get_cat_by_id(cat_id, db)
    if cat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Such cat does not exist")
    return cat


@router.post("/")
async def create_cat(body: CatSchema, db = Depends(get_db)):
    cat = await cats_repository.create_cat(body, db)
    return {"message": f"Cat: {cat.nickname} is created"}
