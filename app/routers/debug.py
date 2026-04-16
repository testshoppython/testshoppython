from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..config import settings
import httpx
import logging

router = APIRouter(
    prefix="/newsletter/debug",
    tags=["Diagnostics"]
)

logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/brevo-status")
async def check_brevo_status():
    """
    Checks if the Brevo API key is configured and tries to connect to the account endpoint.
    Returns details about verified senders and potential errors.
    """
    if not settings.brevo_api_key:
        return {
            "status": "error",
            "message": "BREVO_API_KEY is missing from environment variables.",
            "tip": "Check your Render Dashboard (Environment) or .env file."
        }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.brevo_api_key
    }
    
    results = {}
    
    async with httpx.AsyncClient() as client:
        # 1. Test Account Info
        try:
            res_account = await client.get("https://api.brevo.com/v3/account", headers=headers)
            results["account_connection"] = {
                "status_code": res_account.status_code,
                "data": res_account.json() if res_account.status_code == 200 else res_account.text
            }
        except Exception as e:
            results["account_connection"] = {"error": str(e)}

        # 2. Check Contact Attributes
        try:
            res_attrs = await client.get("https://api.brevo.com/v3/contacts/attributes", headers=headers)
            if res_attrs.status_code == 200:
                attrs = res_attrs.json().get("attributes", [])
                interests_attr = next((a for a in attrs if a["name"] == "INTERESTS"), None)
                results["attributes"] = {
                    "interests_found": interests_attr is not None,
                    "all_attributes": [a["name"] for a in attrs]
                }
            else:
                results["attributes"] = {"error": res_attrs.text}
        except Exception as e:
            results["attributes"] = {"error": str(e)}

        # 3. Check Verified Senders
        try:
            res_senders = await client.get("https://api.brevo.com/v3/senders", headers=headers)
            if res_senders.status_code == 200:
                senders = res_senders.json().get("senders", [])
                results["senders"] = {
                    "verified_list": [s["email"] for s in senders if s["active"]],
                    "total": len(senders)
                }
            else:
                results["senders"] = {"error": res_senders.text}
        except Exception as e:
            results["senders"] = {"error": str(e)}

    return results
