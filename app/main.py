from fastapi import FastAPI, Request, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from . import models
from .routers import products, legal, users, cart, orders, admin, init, auth
from .config import settings
from .i18n import i18n

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OWRE - Premium Storage Solutions",
    description="Premium Aufbewahrungslösungen mit FastAPI und SQLite",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.0.0-rc.77/bundles/redoc.standalone.js",
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        openapi_version="3.0.3",
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.globals.update(i18n=i18n)

app.include_router(init.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(legal.router)
app.include_router(auth.router)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/shop/products", response_class=HTMLResponse)
def products_page(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/shop/product", response_class=HTMLResponse)
def product_page(request: Request, id: int = None, db: Session = Depends(get_db)):
    product = None
    if id:
        product = db.query(models.Product).filter(models.Product.id == id).first()
    return templates.TemplateResponse("product.html", {"request": request, "product": product})


@app.get("/shop/cart", response_class=HTMLResponse)
def cart_page(request: Request):
    return templates.TemplateResponse("cart.html", {"request": request})


@app.get("/shop/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/shop/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/shop/orders", response_class=HTMLResponse)
def orders_page(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request})


@app.get("/shop/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/info/impressum", response_class=HTMLResponse)
def impressum_page(request: Request):
    return templates.TemplateResponse("impressum.html", {"request": request})


@app.get("/info/about", response_class=HTMLResponse)
def about_page(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/health")
def health():
    return {"status": "ok"}