from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import SessionLocal
from .. import models
from ..config import settings
import os
import shutil
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== STATISTICS =====

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

# ===== ORDER MANAGEMENT =====

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

# ===== PRODUCT MANAGEMENT =====

@router.get("/products")
def list_all_products(db: Session = Depends(get_db)):
    """List all products for admin"""
    return db.query(models.Product).all()

@router.post("/products")
async def create_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: int = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Create new product with optional image upload"""
    
    # Verify category exists
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    image_url = None
    
    # Handle file upload
    if file:
        try:
            # Create uploads directory if it doesn't exist
            os.makedirs(settings.upload_dir, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
            filename = timestamp + file.filename
            file_path = os.path.join(settings.upload_dir, filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            image_url = f"/static/uploads/{filename}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File upload failed: {str(e)}"
            )
    
    # Create product
    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        category_id=category_id,
        image_url=image_url,
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return {
        "status": "created",
        "product": db_product,
        "image_url": image_url
    }

@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    stock: int = Form(None),
    category_id: int = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Update product with optional new image"""
    
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields if provided
    if name:
        product.name = name
    if description:
        product.description = description
    if price is not None:
        product.price = price
    if stock is not None:
        product.stock = stock
    if category_id:
        category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        product.category_id = category_id
    
    # Handle new file upload
    if file:
        try:
            # Delete old image if exists
            if product.image_url and product.image_url.startswith("/static/uploads/"):
                old_file_path = product.image_url.replace("/static/uploads/", settings.upload_dir + "/")
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            # Save new file
            os.makedirs(settings.upload_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
            filename = timestamp + file.filename
            file_path = os.path.join(settings.upload_dir, filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            product.image_url = f"/static/uploads/{filename}"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File upload failed: {str(e)}"
            )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return {"status": "updated", "product": product}

@router.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Delete image if exists
    if product.image_url and product.image_url.startswith("/static/uploads/"):
        old_file_path = product.image_url.replace("/static/uploads/", settings.upload_dir + "/")
        if os.path.exists(old_file_path):
            os.remove(old_file_path)
    
    db.delete(product)
    db.commit()
    
    return {"status": "deleted"}

# ===== STOCK MANAGEMENT =====

@router.get("/products/low-stock")
def get_low_stock_products(threshold: int = 5, db: Session = Depends(get_db)):
    """Get products with low stock"""
    products = db.query(models.Product).filter(models.Product.stock <= threshold).all()
    return products

@router.get("/products/popular")
def get_popular_products(limit: int = 10, db: Session = Depends(get_db)):
    """Get most popular products by order count"""
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
            "total_sold": product[3] or 0
        }
        for product in products
    ]

# ===== CATEGORY MANAGEMENT =====

@router.get("/categories")
def list_all_categories(db: Session = Depends(get_db)):
    """List all categories"""
    return db.query(models.Category).all()

@router.post("/categories")
def create_category(name: str = Form(...), description: str = Form(...), db: Session = Depends(get_db)):
    """Create new category"""
    
    db_category = models.Category(name=name, description=description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category

# ===== USER MANAGEMENT =====

@router.get("/users/most-active")
def get_most_active_users(limit: int = 10, db: Session = Depends(get_db)):
    """Get most active users by order count"""
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

@router.get("/users")
def list_all_users(db: Session = Depends(get_db)):
    """List all users"""
    return db.query(models.User).all()

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

# ===== NEWSLETTER MANAGEMENT =====

@router.get("/newsletter/subscribers")
def list_newsletter_subscribers(db: Session = Depends(get_db)):
    """List all newsletter subscribers"""
    return db.query(models.NewsletterSubscriber).order_by(models.NewsletterSubscriber.created_at.desc()).all()

@router.delete("/newsletter/subscribers/{sub_id}")
def delete_subscriber(sub_id: int, db: Session = Depends(get_db)):
    """Delete a subscriber"""
    sub = db.query(models.NewsletterSubscriber).filter(models.NewsletterSubscriber.id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    db.delete(sub)
    db.commit()
    return {"status": "deleted"}

