from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models
from passlib.context import CryptContext

router = APIRouter(prefix="/init", tags=["Initialization"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

@router.post("/seed-data")
def seed_database(db: Session = Depends(get_db)):
    """Initialize database with sample product data"""
    
    # Check if data already exists
    if db.query(models.Category).count() > 0:
        return {"detail": "Database already initialized"}
    
    # Create categories
    categories_data = [
        {"name": "Elektronik", "description": "Computer, Smartphones und Zubehör"},
        {"name": "Kleidung", "description": "Fashion und Bekleidung"},
        {"name": "Bücher", "description": "E-Books und gedruckte Bücher"},
        {"name": "Haushalt", "description": "Haushaltswaren und Dekorationen"},
        {"name": "Sport", "description": "Sportausrüstung und Fitness"},
    ]
    
    categories = []
    for cat_data in categories_data:
        category = models.Category(**cat_data)
        db.add(category)
        categories.append(category)
    db.flush()
    
    # Create products
    products_data = [
        # Elektronik
        {
            "name": "Wireless Kopfhörer",
            "description": "Premium Bluetooth Kopfhörer mit Noise Cancellation",
            "price": 149.99,
            "stock": 50,
            "category_id": categories[0].id,
            "image_url": "https://via.placeholder.com/300?text=Kopfhörer"
        },
        {
            "name": "USB-C Hub",
            "description": "7-in-1 USB-C Hub mit HDMI, USB 3.0 und SD Card Reader",
            "price": 49.99,
            "stock": 100,
            "category_id": categories[0].id,
            "image_url": "https://via.placeholder.com/300?text=USB-Hub"
        },
        {
            "name": "Externe SSD 1TB",
            "description": "Schnelle externe SSD mit 1TB Speicherkapazität",
            "price": 89.99,
            "stock": 30,
            "category_id": categories[0].id,
            "image_url": "https://via.placeholder.com/300?text=SSD"
        },
        # Kleidung
        {
            "name": "Premium T-Shirt",
            "description": "100% Baumwolle, hautfreundlich und langlebig",
            "price": 29.99,
            "stock": 200,
            "category_id": categories[1].id,
            "image_url": "https://via.placeholder.com/300?text=T-Shirt"
        },
        {
            "name": "Laufschuhe Pro",
            "description": "Professionelle Laufschuhe mit Gel-Dämpfung",
            "price": 119.99,
            "stock": 75,
            "category_id": categories[1].id,
            "image_url": "https://via.placeholder.com/300?text=Laufschuhe"
        },
        # Bücher
        {
            "name": "Python Programmierung Grundlagen",
            "description": "Umfassendes Lehrbuch für Python-Anfänger",
            "price": 39.99,
            "stock": 150,
            "category_id": categories[2].id,
            "image_url": "https://via.placeholder.com/300?text=Python+Buch"
        },
        {
            "name": "Web Development mit FastAPI",
            "description": "Modernes Web Development mit Python und FastAPI",
            "price": 49.99,
            "stock": 100,
            "category_id": categories[2].id,
            "image_url": "https://via.placeholder.com/300?text=FastAPI+Buch"
        },
        # Haushalt
        {
            "name": "Küchenorganizer Set",
            "description": "5-teiliges Organisier-Set für die Küche",
            "price": 24.99,
            "stock": 250,
            "category_id": categories[3].id,
            "image_url": "https://via.placeholder.com/300?text=Organizer"
        },
        {
            "name": "LED Schreibtischlampe",
            "description": "Moderne LED Lampe mit 3 Helligkeitsstufen",
            "price": 34.99,
            "stock": 80,
            "category_id": categories[3].id,
            "image_url": "https://via.placeholder.com/300?text=Lampe"
        },
        # Sport
        {
            "name": "Yoga Matte Premium",
            "description": "Rutschfeste Yoga Matte, 6mm dick",
            "price": 44.99,
            "stock": 120,
            "category_id": categories[4].id,
            "image_url": "https://via.placeholder.com/300?text=Yoga+Matte"
        },
        {
            "name": "Hanteln Set 20kg",
            "description": "Verstellbare Hanteln mit Ständer, insgesamt 20kg",
            "price": 79.99,
            "stock": 40,
            "category_id": categories[4].id,
            "image_url": "https://via.placeholder.com/300?text=Hanteln"
        },
    ]
    
    for product_data in products_data:
        product = models.Product(**product_data)
        db.add(product)
    db.flush()
    
    # Create admin user
    admin_user = models.User(
        email="admin@testshop.de",
        username="admin",
        firstname="Admin",
        lastname="User",
        hashed_password=hash_password("admin123"),
        is_admin=True,
        is_active=True
    )
    db.add(admin_user)
    db.flush()
    
    # Create admin cart
    admin_cart = models.Cart(user_id=admin_user.id)
    db.add(admin_cart)
    
    # Create demo user
    demo_user = models.User(
        email="demo@testshop.de",
        username="demo",
        firstname="Demo",
        lastname="User",
        phone="+49 123 456789",
        hashed_password=hash_password("demo123"),
        is_active=True
    )
    db.add(demo_user)
    db.flush()
    
    # Create demo cart
    demo_cart = models.Cart(user_id=demo_user.id)
    db.add(demo_cart)
    
    # Create demo address
    demo_address = models.Address(
        user_id=demo_user.id,
        street="Beispielstraße 123",
        city="Berlin",
        postal_code="10115",
        country="Deutschland",
        is_default=True
    )
    db.add(demo_address)
    
    db.commit()
    
    return {
        "detail": "Database initialized successfully",
        "categories_created": len(categories_data),
        "products_created": len(products_data),
        "admin_user": "admin@testshop.de (Password: admin123)",
        "demo_user": "demo@testshop.de (Password: demo123)"
    }

@router.get("/check-data")
def check_database(db: Session = Depends(get_db)):
    """Check database initialization status"""
    return {
        "categories": db.query(models.Category).count(),
        "products": db.query(models.Product).count(),
        "users": db.query(models.User).count(),
        "orders": db.query(models.Order).count(),
        "carts": db.query(models.Cart).count(),
    }
