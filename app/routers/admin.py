from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stats")
def get_shop_statistics(db: Session = Depends(get_db)):
    """Get general shop statistics"""
    total_products = db.query(models.Product).count()
    total_users = db.query(models.User).count()
    total_orders = db.query(models.Order).count()
    total_revenue = 0
    
    orders = db.query(models.Order).all()
    for order in orders:
        if order.status in ["paid", "shipped", "delivered"]:
            total_revenue += order.total_price
    
    return {
        "total_products": total_products,
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "users_today": db.query(models.User).count(),
    }

@router.get("/orders/pending")
def get_pending_orders(db: Session = Depends(get_db)):
    """Get all pending orders"""
    orders = db.query(models.Order).filter(models.Order.status == "pending").all()
    return orders

@router.get("/orders/revenue")
def get_revenue_info(db: Session = Depends(get_db)):
    """Get revenue information"""
    orders = db.query(models.Order).all()
    
    revenue_by_status = {}
    for status in ["pending", "paid", "shipped", "delivered", "cancelled"]:
        revenue_by_status[status] = 0
    
    total_revenue = 0
    for order in orders:
        revenue_by_status[order.status] += order.total_price
        if order.status in ["paid", "shipped", "delivered"]:
            total_revenue += order.total_price
    
    return {
        "total_revenue": total_revenue,
        "revenue_by_status": revenue_by_status,
        "total_orders": len(orders),
    }

@router.get("/products/low-stock")
def get_low_stock_products(threshold: int = 5, db: Session = Depends(get_db)):
    """Get products with low stock"""
    products = db.query(models.Product).filter(models.Product.stock <= threshold).all()
    return products

@router.get("/users/most-active")
def get_most_active_users(limit: int = 10, db: Session = Depends(get_db)):
    """Get most active users by order count"""
    from sqlalchemy import func
    users = db.query(
        models.User.id,
        models.User.username,
        models.User.email,
        func.count(models.Order.id).label("order_count")
    ).join(models.Order).group_by(models.User.id).order_by(
        func.count(models.Order.id).desc()
    ).limit(limit).all()
    
    return [
        {
            "user_id": user[0],
            "username": user[1],
            "email": user[2],
            "order_count": user[3]
        }
        for user in users
    ]

@router.get("/products/popular")
def get_popular_products(limit: int = 10, db: Session = Depends(get_db)):
    """Get most popular products by order count"""
    from sqlalchemy import func
    products = db.query(
        models.Product.id,
        models.Product.name,
        models.Product.price,
        func.sum(models.OrderItem.quantity).label("total_sold")
    ).join(models.OrderItem).group_by(models.Product.id).order_by(
        func.sum(models.OrderItem.quantity).desc()
    ).limit(limit).all()
    
    return [
        {
            "product_id": product[0],
            "name": product[1],
            "price": product[2],
            "total_sold": product[3]
        }
        for product in products
    ]

@router.delete("/clear-all-data")
def clear_all_data(confirm: str = None, db: Session = Depends(get_db)):
    """DANGER: Clear all data from database - requires confirmation"""
    if confirm != "YES_DELETE_ALL":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Confirmation required. Send confirm="YES_DELETE_ALL" parameter'
        )
    
    db.query(models.OrderItem).delete()
    db.query(models.CartItem).delete()
    db.query(models.Order).delete()
    db.query(models.Cart).delete()
    db.query(models.Address).delete()
    db.query(models.User).delete()
    db.query(models.Product).delete()
    db.query(models.Category).delete()
    db.commit()
    
    return {"detail": "All data deleted"}
