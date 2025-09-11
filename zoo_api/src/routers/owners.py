from fastapi import Depends, APIRouter, HTTPException, status
from src.repository import owners as owners_repository
from src.schemas.owners import OwnerSchema
from src.database.db import get_db
from src.roles import RoleAccess, Role
router = APIRouter(prefix="/owners", tags=['owners'])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator])
admin_only = RoleAccess([Role.admin])



@router.get("/", dependencies=Depends(admin_only))
async def get_owners_list(db = Depends(get_db)):
    owners = await owners_repository.get_owners(db)
    return owners

@router.get("/{owner_id}")
async def get_cat(owner_id:int, db = Depends(get_db)):
    cat = await owners_repository.get_owner_by_id(owner_id, db)
    if cat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Such owner does not exist")
    return cat


@router.post("/")
async def create_owner(body: OwnerSchema, db = Depends(get_db)):
    owner = await owners_repository.create_owner(body, db)
    return {"message": f"Owner: {owner.id} is created"}
