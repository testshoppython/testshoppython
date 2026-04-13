from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import Base, engine
from .routers import products, legal, users, cart, orders, admin, init

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TestShopPython - E-Commerce API",
    description="Kompletter Online-Shop mit Python und FastAPI",
    version="1.0.0",
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(init.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(legal.router)

@app.get("/")
def home():
    return {
        "message": "Willkommen zur TestShopPython API!",
        "version": "1.0.0",
        "endpoints": {
            "products": "/products/",
            "users": "/users/",
            "cart": "/cart/",
            "orders": "/orders/",
            "admin": "/admin/",
            "legal": "/info/",
            "init": "/init/"
        },
        "documentation": "/docs/",
        "initialization": "POST /init/seed-data"
    }

@app.get("/health")
def health():
    return {"status": "ok"}