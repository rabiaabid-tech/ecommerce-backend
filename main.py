# main.py
from fastapi import FastAPI
from database import engine
import models
from routers import products, auth
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Automatically generate database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="E-commerce API", version="1.0.0")

origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"  # default fallback
).split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints
app.include_router(products.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "Active", "message": "E-commerce Backend is running successfully!"}