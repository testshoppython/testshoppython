from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/cart", tags=["Cart"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{user_id}", response_model=schemas.Cart)
def get_cart(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warenkorb nicht gefunden"
        )
    return cart

@router.post("/{user_id}/items", response_model=schemas.CartItem)
def add_to_cart(user_id: int, item: schemas.CartItemCreate, db: Session = Depends(get_db)):
    # Get or create cart
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        cart = models.Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    # Check if product exists
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produkt nicht gefunden"
        )
    
    # Check if item already in cart
    cart_item = db.query(models.CartItem).filter(
        (models.CartItem.cart_id == cart.id) &
        (models.CartItem.product_id == item.product_id)
    ).first()
    
    if cart_item:
        cart_item.quantity += item.quantity
        db.add(cart_item)
    else:
        db_cart_item = models.CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(db_cart_item)
    
    db.commit()
    cart_item = db.query(models.CartItem).filter(
        (models.CartItem.cart_id == cart.id) &
        (models.CartItem.product_id == item.product_id)
    ).first()
    db.refresh(cart_item)
    return cart_item

@router.put("/{user_id}/items/{item_id}", response_model=schemas.CartItem)
def update_cart_item(user_id: int, item_id: int, item_update: schemas.CartItemCreate, db: Session = Depends(get_db)):
    # Verify cart belongs to user
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warenkorb nicht gefunden"
        )
    
    cart_item = db.query(models.CartItem).filter(
        (models.CartItem.id == item_id) &
        (models.CartItem.cart_id == cart.id)
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warenkorbposition nicht gefunden"
        )
    
    if item_update.quantity <= 0:
        db.delete(cart_item)
    else:
        cart_item.quantity = item_update.quantity
        db.add(cart_item)
    
    db.commit()
    
    if item_update.quantity <= 0:
        return None
    
    db.refresh(cart_item)
    return cart_item

@router.delete("/{user_id}/items/{item_id}")
def remove_from_cart(user_id: int, item_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warenkorb nicht gefunden"
        )
    
    cart_item = db.query(models.CartItem).filter(
        (models.CartItem.id == item_id) &
        (models.CartItem.cart_id == cart.id)
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warenkorbposition nicht gefunden"
        )
    
    db.delete(cart_item)
    db.commit()
    return {"detail": "Artikel entfernt"}

@router.delete("/{user_id}/clear")
def clear_cart(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warenkorb nicht gefunden"
        )
    
    db.query(models.CartItem).filter(models.CartItem.cart_id == cart.id).delete()
    db.commit()
    return {"detail": "Warenkorb geleert"}

@router.get("/{user_id}/total")
def get_cart_total(user_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.user_id == user_id).first()
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warenkorb nicht gefunden"
        )
    
    total = 0
    item_count = 0
    for item in cart.items:
        total += item.product.price * item.quantity
        item_count += item.quantity
    
    return {
        "total_price": total,
        "item_count": item_count,
        "items_count": len(cart.items)
    }
