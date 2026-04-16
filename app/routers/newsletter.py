from fastapi import APIRouter, HTTPException, status, Depends
import httpx
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import SessionLocal
from ..config import settings
import logging

router = APIRouter(
    prefix="/newsletter",
    tags=["Newsletter"]
)

logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

WELCOME_EMAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: 'Montserrat', sans-serif; line-height: 1.6; color: #1a1a1a; margin: 0; padding: 0; background-color: #fafafa; }
        .container { max-width: 600px; margin: 0 auto; background-color: #ffffff; }
        .header { background-color: #f7f2e8; padding: 40px; text-align: center; }
        .header h1 { color: #c9a961; font-weight: 500; margin: 0; letter-spacing: 2px; }
        .content { padding: 40px; text-align: center; }
        .discount-box { background-color: #f9f9f9; border: 1px dashed #c9a961; padding: 20px; margin: 30px 0; }
        .code { font-size: 24px; font-weight: 700; color: #1a1a1a; letter-spacing: 5px; }
        .footer { padding: 30px; text-align: center; font-size: 12px; color: #999; }
        .btn { background-color: #1a1a1a; color: #ffffff !important; padding: 15px 30px; text-decoration: none; display: inline-block; font-weight: 500; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>OWRE</h1>
        </div>
        <div class="content">
            <h2>Willkommen in der Community!</h2>
            <p>Schön, dass du dabei bist. Bei OWRE dreht sich alles um die feinen Details, die ein Zuhause erst zu einem persönlichen Rückzugsort machen.</p>
            <p>Als Dankeschön für dein Vertrauen schenken wir dir 10% Rabatt auf deine erste Bestellung.</p>
            
            <div class="discount-box">
                <p style="margin: 0 0 10px 0; font-size: 14px; color: #666;">DEIN GUTSCHEINCODE:</p>
                <div class="code">WELCOME10</div>
            </div>
            
            <a href="https://owre.shop" class="btn">JETZT SHOPPEN</a>
            
            <p style="margin-top: 40px; font-size: 14px; color: #666;">Viel Freude beim Stöbern!</p>
        </div>
        <div class="footer">
            &copy; 2026 OWRE Lifestyle. Alle Rechte vorbehalten.<br>
            Du erhältst diese E-Mail, weil du dich auf owre.shop für unseren Newsletter angemeldet hast.
        </div>
    </div>
</body>
</html>
"""

async def send_welcome_email(email: str):
    """Sends a transactional welcome email via Brevo"""
    if not settings.brevo_api_key: return f"Skipped (No API Key)"
    
    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.brevo_api_key
    }
    
    payload = {
        "sender": {"name": "OWRE Team", "email": "maxim.shushanikov@gfn.education"},
        "to": [{"email": email}],
        "subject": "Willkommen bei OWRE – Dein Geschenk wartet",
        "htmlContent": WELCOME_EMAIL_HTML
    }



    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code >= 400:
                logger.error(f"Brevo Email Error: {response.status_code} - {response.text}")
            return response.status_code
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return str(e)


@router.post("/subscribe")
async def subscribe_newsletter(request: schemas.NewsletterSubscribeRequest, db: Session = Depends(get_db)):
    # 1. Local Database Save
    subscriber = db.query(models.NewsletterSubscriber).filter(models.NewsletterSubscriber.email == request.email).first()
    if not subscriber:
        new_sub = models.NewsletterSubscriber(
            email=request.email,
            interests=", ".join(request.interests) if request.interests else ""
        )
        db.add(new_sub)
        db.commit()

    # 2. Brevo Contact Sync
    if settings.brevo_api_key:
        contact_url = "https://api.brevo.com/v3/contacts"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": settings.brevo_api_key
        }
        
        payload = {
            "email": request.email,
            "updateEnabled": True,
            "attributes": {
                "INTERESTS": ", ".join(request.interests) if request.interests else "None"
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Sync Contact
                res_contact = await client.post(contact_url, json=payload, headers=headers)
                logger.info(f"Brevo Contact Sync: {res_contact.status_code} - {res_contact.text}")
                
                # 3. Trigger Welcome Email
                res_email = await send_welcome_email(request.email)
                logger.info(f"Brevo Welcome Email Status: {res_email}")
                
        except Exception as exc:
            logger.error(f"Brevo integration error: {exc}")

            # We don't fail the whole request if Brevo fails, as long as we saved locally?
            # Actually, standard behavior is to notify success if at least one worked.

    return {"message": "Successfully subscribed to the newsletter!"}

