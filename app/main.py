import os
from fastapi import FastAPI
from .routers import identify
from .database import engine
from dotenv import load_dotenv

load_dotenv(".env")

app = FastAPI()

from fastapi import HTTPException
from sqlalchemy import text

@app.get("/")
async def func():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT datname FROM pg_database;")).fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "online", "databases": [row[0] for row in result]}

app.include_router(identify.router)
