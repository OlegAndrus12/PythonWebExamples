from fastapi import Depends, APIRouter, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from src.database.db import get_db
from src.schemas.users import UserRegisterSchema, UserResponseSchema, RequestEmail
from src.repository import auth as auth_repository
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=['auth'])

@router.post("/signup", response_model=UserResponseSchema)
async def signup(body:UserRegisterSchema, background_tasks: BackgroundTasks, request: Request, db = Depends(get_db)):
    user = await auth_repository.get_user_by_email(body.email, db)
    if user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    body.password = await auth_service.hash_password(body.password)
    user = await auth_repository.create_user(body, db)
    background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return user

@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = await auth_repository.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email is not verified")
    if not await auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    access_token = await auth_service.create_jwt_token(payload={"user_email": user.email})
    return {"access_token": access_token}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db = Depends(get_db)):
    email = await auth_service.decode_verification_token(token)
    user = await auth_repository.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    
    await auth_repository.change_confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db = Depends(get_db)):
    user = await auth_repository.get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            return {"message": "Your email is already confirmed"}
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}