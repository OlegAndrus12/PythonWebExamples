from passlib.context import CryptContext
import redis
import pickle
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # jwt auth
from datetime import datetime, timezone, timedelta
from src.database.db import get_db
from src.repository.auth import get_user_by_email
from src.settings import settings
# json web token


class AuthService:
    ALGORITHM = "HS256"
    pwd_context = CryptContext(schemes=["bcrypt"])
    oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    redis_client = redis.Redis(host="redis", port=6379)

    async def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    async def hash_password(self, password: str):
        return self.pwd_context.hash(password)
    
    async def create_jwt_token(self, payload:dict, scope="access_token", expires_delta: float = 15):
        payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
        payload["scope"] = scope
        token = jwt.encode(payload, settings.secret_key, algorithm=self.ALGORITHM)
        return token
    
    async def decode_verification_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'verification_token':
                email = payload['email']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")

    
    async def get_current_user(self, token = Depends(oauth2_schema), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        try:
            payload = jwt.decode(token, settings.secret_key, self.ALGORITHM)
            if payload.get("scope") == "access_token":
                email = payload.get("user_email")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except:
            raise credentials_exception
        
        user_redis_key = f"email:{email}"
        user = self.redis_client.get(user_redis_key)
        if user is None:
            print("No user, lets call db")
            user = await get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
    
            self.redis_client.set(user_redis_key, pickle.dumps(user), ex=10 * 60)        
        else:
            print("getting from the redis cache")
            user = pickle.loads(user)

        return user
    

auth_service = AuthService()
