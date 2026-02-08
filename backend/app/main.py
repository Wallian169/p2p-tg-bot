from fastapi import FastAPI
from app.routers.currencies import currency_router
from app.routers.users import user_router

app = FastAPI()
app.include_router(router=currency_router)
app.include_router(router=user_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
