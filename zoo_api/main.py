
from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from src.routers import cats, owners, auth
from src.database.db import get_db

app = FastAPI()


@app.get("/api/healthchecker")
async def healthchecker(db = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1 + 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database is not configured correctly")
        return {"message": "API is up and running"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database is not configured correctly")

@app.get("/")
async def index():
    return {"message": "Welcome to zoo api!"}

ALLOWED_IPS = ['192.168.1.0']


@app.middleware("http")
async def limit_access_by_ip(request, call_next):
    # before server got the request

    await call_next(request)

    # after server responded

    ip = request.client.host
    if ip not in ALLOWED_IPS:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "Not allowed IP address"})
    response = await call_next(request)
    return response


app.include_router(cats.router, prefix="/api")
app.include_router(owners.router, prefix="/api")
app.include_router(auth.router, prefix="/api")

# postgress
# migrations: alembic
# orm: sqlalchemy
# async python server: fastapi
# dependency: poetry
# settings/config: pydantic-settings
# schemas/validation: pydantic
# redis
# celery
# smtp server for email
# docker compose