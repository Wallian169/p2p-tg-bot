from fastapi import FastAPI
from app.routers.currencies import currency_router

app = FastAPI()
app.include_router(router=currency_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
