from fastapi import FastAPI
from database.db import connectDB
from app.routes import router

app = FastAPI()

#  connecting Database on Startup
connectDB()


app.include_router(router,prefix="/api",tags=["blogs"])

@app.get("/")
def read_root():
    return {"Hello": "World"}


