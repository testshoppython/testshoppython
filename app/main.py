from fastapi import FastAPI
from .database import Base, engine
from .routers import products, legal

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TestShopPython")

app.include_router(products.router)
app.include_router(legal.router)

@app.get("/")
def home():
    return {"message": "Welcome to TestShopPython API!"}