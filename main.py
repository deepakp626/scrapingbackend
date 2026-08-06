from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import connectDB
from app.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

#  connecting Database on Startup
connectDB()


app.include_router(router,prefix="/api",tags=["blogs"])

@app.get("/")
def read_root():
    return {"Hello": "World"}


