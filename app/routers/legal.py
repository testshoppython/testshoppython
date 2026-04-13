from fastapi import APIRouter

router = APIRouter(prefix="/info", tags=["Legal"])

@router.get("/impressum")
def impressum():
    return {
        "unternehmen": "Dein Firmenname",
        "adresse": "Straße 1, 12345 Musterstadt, Deutschland",
        "vertreter": "Maxim Shushanikov",
        "kontakt": {
            "email": "kontakt@deine-domain.de",
            "telefon": "+49 123 456789"
        }
    }