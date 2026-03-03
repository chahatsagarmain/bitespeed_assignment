import logging
from fastapi import FastAPI
from .routers import identify
from .database import engine, Base
from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import text

# load environment variables
load_dotenv(".env")
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

app = FastAPI(debug=True)
Base.metadata.create_all(bind=engine)

@app.get("/")
async def func():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT datname FROM pg_database;")).fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "online", "databases": [row[0] for row in result]}


@app.exception_handler(Exception)
async def all_exceptions(request, exc):
    logging.getLogger("app").exception("Unhandled exception")
    return HTTPException(status_code=500, detail=str(exc))

app.include_router(identify.router)
