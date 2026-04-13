from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas
from datetime import datetime
import uuid

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.Order])
def list_orders(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestellung nicht gefunden"
        )
    return order

@router.get("/user/{user_id}", response_model=list[schemas.Order])
def get_user_orders(user_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    orders = db.query(models.Order).filter(
        models.Order.user_id == user_id
    ).offset(skip).limit(limit).all()
    return orders

@router.post("/", response_model=schemas.Order)
def create_order(user_id: int, order: schemas.OrderCreate, db: Session = Depends(get_db)):
    # Check user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User nicht gefunden"
        )
    
    # Get cart
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart or len(cart.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warenkorb ist leer"
        )
    
    # Calculate total price
    total_price = 0
    order_items = []
    for item in cart.items:
        product = item.product
        total_price += product.price * item.quantity
        order_items.append({
            'product_id': product.id,
            'quantity': item.quantity,
            'price': product.price
        })
    
    # Create order
    order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    shipping_address_id = None
    if order.shipping_address_id:
        shipping_address = db.query(models.Address).filter(
            models.Address.id == order.shipping_address_id,
            models.Address.user_id == user_id
        ).first()
        if not shipping_address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Versandadresse nicht gefunden"
            )
        shipping_address_id = order.shipping_address_id

    db_order = models.Order(
        user_id=user_id,
        order_number=order_number,
        total_price=total_price,
        payment_method=order.payment_method,
        shipping_address_id=shipping_address_id,
        status="pending"
    )
    db.add(db_order)
    db.flush()
    
    # Add order items
    for order_item_data in order_items:
        db_order_item = models.OrderItem(
            order_id=db_order.id,
            product_id=order_item_data['product_id'],
            quantity=order_item_data['quantity'],
            price=order_item_data['price']
        )
        db.add(db_order_item)
    
    # Clear cart
    db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).delete()
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.put("/{order_id}", response_model=schemas.Order)
def update_order_status(order_id: int, order_update: schemas.OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestellung nicht gefunden"
        )
    
    # Validate status
    valid_statuses = ["pending", "paid", "shipped", "delivered", "cancelled"]
    if order_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ungültiger Status. Erlaubte Werte: {valid_statuses}"
        )
    
    order.status = order_update.status
    order.updated_at = datetime.utcnow()
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.delete("/{order_id}")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestellung nicht gefunden"
        )
    
    if order.status not in ["pending", "paid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bestellung kann nicht storniert werden"
        )
    
    order.status = "cancelled"
    order.updated_at = datetime.utcnow()
    db.add(order)
    db.commit()
    return {"detail": "Bestellung storniert"}

@router.get("/by-number/{order_number}", response_model=schemas.Order)
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_number == order_number).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bestellung nicht gefunden"
        )
    return order
