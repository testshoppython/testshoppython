from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .database import Base, engine
from .routers import products, legal, users, cart, orders, admin, init, auth
from .config import settings
from .i18n import i18n

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OWRE - Premium Storage Solutions",
    description="Premium Aufbewahrungslösungen mit FastAPI und SQLite",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Set global template context
@app.middleware("http")
async def add_i18n_to_context(request: Request, call_next):
    language = request.query_params.get("lang", settings.default_language)
    i18n.set_language(language)
    request.state.i18n = i18n
    request.state.lang = language
    response = await call_next(request)
    return response

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
    return templates.TemplateResponse("index.html", {
        "request": request,
        "i18n": i18n,
        "settings": settings
    })

@app.get("/shop/products", response_class=HTMLResponse)
def products_page(request: Request):
    return templates.TemplateResponse("products.html", {
        "request": request,
        "i18n": i18n,
        "settings": settings
    })

@app.get("/shop/product", response_class=HTMLResponse)
def product_page(request: Request):
    return templates.TemplateResponse("product.html", {
        "request": request,
        "i18n": i18n,
        "settings": settings
    })

@app.get("/shop/cart", response_class=HTMLResponse)
def cart_page(request: Request):
    return templates.TemplateResponse("cart.html", {
        "request": request,
        "i18n": i18n,
        "settings": settings
    })

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "i18n": i18n,
        "settings": settings
    })

@app.get("/user/orders", response_class=HTMLResponse)
def orders_page(request: Request):
    return templates.TemplateResponse("orders.html", {
        "request": request,
        "i18n": i18n,
        "settings": settings
    })

@app.get("/user/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {
        "request": request,
        "i18n": i18n,
        "settings": settings
    })

@app.get("/user/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "i18n": i18n,
        "settings": settings
    })

@app.get("/health")
def health():
    return {"status": "ok"}