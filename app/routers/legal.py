from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/info", tags=["Legal"])
templates = Jinja2Templates(directory="templates")

@router.get("/impressum", response_class=HTMLResponse)
def impressum_page(request: Request):
    return templates.TemplateResponse("impressum.html", {"request": request})

@router.get("/shipping", response_class=HTMLResponse)
def shipping_page(request: Request):
    """Versandinformationen"""
    return templates.TemplateResponse("shipping.html", {"request": request})

@router.get("/returns", response_class=HTMLResponse)
def returns_page(request: Request):
    """Rückgabe & Widerruf"""
    return templates.TemplateResponse("returns.html", {"request": request})

@router.get("/privacy", response_class=HTMLResponse)
def privacy_page(request: Request):
    """Datenschutzerklärung"""
    return templates.TemplateResponse("privacy.html", {"request": request})

@router.get("/terms", response_class=HTMLResponse)
def terms_page(request: Request):
    """Allgemeine Geschäftsbedingungen"""
    return templates.TemplateResponse("terms.html", {"request": request})

@router.get("/contact", response_class=HTMLResponse)
def contact_page(request: Request):
    """Kontaktseite"""
    return templates.TemplateResponse("contact.html", {"request": request})

# API-Endpoints (für mobile Apps etc.)
@router.get("/api/shipping")
def shipping_information():
    return {
        "shipping_methods": [
            {
                "method": "Standard (DHL)",
                "cost": 5.99,
                "delivery_time": "2-3 Werktage",
                "free_above": 50.00
            },
            {
                "method": "Express (DHL)",
                "cost": 9.99,
                "delivery_time": "1 Werktag"
            }
        ],
        "service": "service@owre.shop"
    }

@router.get("/api/contact")
def contact_information():
    return {
        "company": "OWRE GmbH",
        "email": "contact@owre.shop",
        "phone": "+49 30 12345678",
        "hours": "Mo-Fr 9:00-17:00 Uhr",
        "address": "Musterstraße 12, 10115 Berlin, Deutschland",
        "response_time": "24 Stunden"
    }