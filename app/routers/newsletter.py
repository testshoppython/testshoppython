from fastapi import APIRouter, HTTPException, status
import httpx
from .. import schemas
from ..config import settings
import logging

router = APIRouter(
    prefix="/newsletter",
    tags=["Newsletter"]
)

logger = logging.getLogger(__name__)

@router.post("/subscribe")
async def subscribe_newsletter(request: schemas.NewsletterSubscribeRequest):
    if not settings.brevo_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Newsletter service is currently not configured."
        )

    # Brevo API URL for creating a contact
    url = "https://api.brevo.com/v3/contacts"
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.brevo_api_key
    }
    
    payload = {
        "email": request.email,
        "updateEnabled": True, # If they exist, update them
        "attributes": {
            "INTERESTS": ", ".join(request.interests) if request.interests else "None"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            
            # Brevo returns 201 Created on success, 204 No Content for update
            if response.status_code in [201, 204]:
                return {"message": "Successfully subscribed to the newsletter!"}
            else:
                logger.error(f"Brevo API error: {response.status_code} - {response.text}")
                res_data = response.json()
                if "message" in res_data:
                    raise HTTPException(status_code=400, detail=res_data["message"])
                raise HTTPException(status_code=400, detail="Failed to subscribe.")
                
    except httpx.RequestError as exc:
        logger.error(f"HTTP Exception for {exc.request.url} - {exc}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Network error while contacting newsletter service.")
