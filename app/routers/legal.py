from fastapi import APIRouter

router = APIRouter(prefix="/legal", tags=["Legal"])

@router.get("/impressum")
def impressum():
    return {
        "shop_name": "OWRE",
        "company": "OWRE GmbH",
        "address": "Mustergasse 12, 10115 Berlin, Deutschland",
        "representing": "Max Mustermann",
        "contact": {
            "email": "info@owre.shop",
            "phone": "+49 30 12345678",
            "website": "https://owre.shop"
        },
        "tax_id": "DE123456789",
        "commercial_register": "HRB 123456",
        "responsible_content": "Max Mustermann"
    }

@router.get("/imprint")
def imprint():
    """English version of Impressum"""
    return impressum()

@router.get("/terms")
def terms_and_conditions():
    return {
        "terms": [
            {
                "section": "1. Allgemeines",
                "content": "Die folgenden Bedingungen regeln die Nutzung dieses Online-Shops."
            },
            {
                "section": "2. Vertragsabschluss",
                "content": "Mit der Bestellung erklären Sie sich mit unseren Bedingungen einverstanden."
            },
            {
                "section": "3. Preise und Verfügbarkeit",
                "content": "Alle Preise verstehen sich inkl. 19% MwSt. Änderungen vorbehalten."
            },
            {
                "section": "4. Lieferung",
                "content": "Lieferung erfolgt per DHL innerhalb von 2-3 Werktagen."
            },
            {
                "section": "5. Zahlungsbedingungen",
                "content": "Zahlung erfolgt per Kreditkarte, PayPal oder Lastschrift."
            },
            {
                "section": "6. Rückgaberecht",
                "content": "Rückgabe innerhalb von 14 Tagen ab Kaufdatum möglich."
            }
        ]
    }

@router.get("/privacy")
def privacy_policy():
    return {
        "privacy": [
            {
                "section": "1. Datenschutz",
                "content": "Ihre Daten werden verschlüsselt und sicher gespeichert."
            },
            {
                "section": "2. Verarbeitung personenbezogener Daten",
                "content": "Wir verarbeiten Ihre Daten nur für die Abwicklung Ihrer Bestellung."
            },
            {
                "section": "3. Cookies",
                "content": "Diese Website verwendet Cookies zur Verbesserung der Benutzerfreundlichkeit."
            },
            {
                "section": "4. Ihre Rechte",
                "content": "Sie haben das Recht auf Auskunft, Berichtigung und Löschung Ihrer Daten."
            }
        ]
    }

@router.get("/shipping")
def shipping_information():
    return {
        "shipping_methods": [
            {
                "method": "Standard (DHL)",
                "cost": 5.99,
                "delivery_time": "2-3 Werktage"
            },
            {
                "method": "Express (DHL)",
                "cost": 9.99,
                "delivery_time": "1 Werktag"
            },
            {
                "method": "Free Shipping",
                "cost": 0,
                "delivery_time": "3-5 Werktage",
                "conditions": "ab 50€ Bestellwert"
            }
        ],
        "service": "service@testshop.de"
    }

@router.get("/contact")
def contact_information():
    return {
        "company": "OWRE GmbH",
        "email": "contact@owre.shop",
        "phone": "+49 30 12345678",
        "hours": "Mo-Fr 9:00-17:00 Uhr",
        "address": "Mustergasse 12, 10115 Berlin, Deutschland",
        "response_time": "24 Stunden"
    }