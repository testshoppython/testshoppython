from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from ..config import settings
import stripe
import logging

router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)

logger = logging.getLogger(__name__)

# Configure Stripe
if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: Request,
    user_id: int, 
    promo_code: str = None,
    db: Session = Depends(get_db)
):
    if not settings.stripe_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe credentials not configured."
        )

    # Get cart for user
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    cart_items = cart.items

    line_items = []
    total_amount = 0
    
    for item in cart_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            continue
            
        total_amount += product.price * item.quantity
        
        line_items.append({
            "price_data": {
                "currency": "eur",
                "unit_amount": int(product.price * 100), # Stripe uses cents
                "product_data": {
                    "name": product.name,
                    "description": product.description[:250] if product.description else "Premium Produkt",
                },
            },
            "quantity": item.quantity,
        })
        
    # Add shipping if applicable
    if total_amount < 50:
        line_items.append({
            "price_data": {
                "currency": "eur",
                "unit_amount": 499,
                "product_data": {
                    "name": "Standardversand",
                },
            },
            "quantity": 1,
        })

    # Apply discount
    discounts = []
    if promo_code:
        from .cart import VALID_COUPONS
        code = promo_code.upper().strip()
        if code in VALID_COUPONS:
            c = VALID_COUPONS[code]
            try:
                if c["type"] == "percent":
                    stripe_coupon = stripe.Coupon.create(percent_off=c["value"], duration="once")
                else:
                    stripe_coupon = stripe.Coupon.create(amount_off=int(c["value"]*100), currency="eur", duration="once")
                discounts = [{"coupon": stripe_coupon.id}]
            except Exception as ev:
                logger.error(f"Error creating stripe coupon: {str(ev)}")

    # Prepare success/cancel URLs based on the request origin
    domain_url = f"{request.url.scheme}://{request.url.netloc}"
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card", "paypal", "klarna"], # Enable popular methods
            line_items=line_items,
            mode="payment",
            discounts=discounts if discounts else None,
            success_url=domain_url + "/shop/profile?session_id={CHECKOUT_SESSION_ID}&success=true",
            cancel_url=domain_url + "/shop/cart?canceled=true",
            client_reference_id=str(user_id)
        )
        return {"checkout_url": checkout_session.url}
    except Exception as e:
        logger.error(f"Error creating Stripe checkout session: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
