
from fastapi import FastAPI
from app.routers import tuning

app = FastAPI()

app.include_router(tuning.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Signal Tuning API"}