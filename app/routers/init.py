from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models
from .users import hash_password, get_db

router = APIRouter(prefix="/init", tags=["Initialization"])

@router.post("/seed-data")
def seed_database(db: Session = Depends(get_db)):
    """Initialize database with OWRE product data"""
    
    # Check if data already exists
    if db.query(models.Category).count() > 0:
        return {"detail": "Database already initialized"}
    
    # Create OWRE categories
    categories_data = [
        {"name": "Große Aufbewahrungsboxen", "description": "Geräumige Boxen mit stilvollem Design für größere Gegenstände"},
        {"name": "Kleine Aufbewahrungskörbe", "description": "Kompakte Körbe für Organisation und Ordnung"},
        {"name": "Stoff-Behälter", "description": "Weiches Material für sanfte Aufbewahrung"},
        {"name": "Sets & Bundles", "description": "Komplette Lösungen für verschiedene Räume"},
        {"name": "Zubehör", "description": "Ergänzungen und Zubehör für perfekte Organisation"},
    ]
    
    categories = []
    for cat_data in categories_data:
        category = models.Category(**cat_data)
        db.add(category)
        categories.append(category)
    db.flush()
    
    # Create OWRE products with local images
    products_data = [
        # Große Aufbewahrungsboxen
        {
            "name": "OWRE Premium Aufbewahrungsbox Groß",
            "description": "Premium Aufbewahrungsbox aus robustem Material mit modernem Design. Perfekt für Wohnzimmer, Schlafzimmer oder Kinderzimmer.",
            "price": 49.99,
            "stock": 50,
            "category_id": categories[0].id,
            "image_url": "/static/images/baskets_001.png"
        },
        {
            "name": "OWRE Storage Lux - Große Variante",
            "description": "Elegante große Aufbewahrungsbox mit hochwertigen Griffen und stabilem Rahmen. Ideal zur Aufbewahrung von Decken, Accessoires oder Spielzeug.",
            "price": 59.99,
            "stock": 40,
            "category_id": categories[0].id,
            "image_url": "/static/images/baskets_002.png"
        },
        {
            "name": "OWRE Raumwunder Box",
            "description": "Raumsparende Design-Box für intelligente Aufbewahrung. Mit praktischen Trennern und großem Fassungsvermögen.",
            "price": 69.99,
            "stock": 30,
            "category_id": categories[0].id,
            "image_url": "/static/images/room_001.png"
        },
        # Kleine Aufbewahrungskörbe
        {
            "name": "OWRE Mini Korb Set (2er)",
            "description": "Zwei kleine Aufbewahrungskörbe im Set. Perfekt für Schreibtisch, Nachttisch oder Regal.",
            "price": 24.99,
            "stock": 100,
            "category_id": categories[1].id,
            "image_url": "/static/images/baskets_003.png"
        },
        {
            "name": "OWRE Compact Organizer",
            "description": "Kompakter Korb mit mehreren Fächern für perfekte Dekoration und Ordnung.",
            "price": 34.99,
            "stock": 75,
            "category_id": categories[1].id,
            "image_url": "/static/images/room_002.png"
        },
        # Stoff-Behälter
        {
            "name": "OWRE Stoff-Container Premium",
            "description": "Weicher Stoff-Container in zeitlosem Grau. Leichtgewichtig aber stabil, perfekt für empfindliche Gegenstände.",
            "price": 39.99,
            "stock": 60,
            "category_id": categories[2].id,
            "image_url": "/static/images/baskets_001.png"
        },
        {
            "name": "OWRE Textil Box Deluxe",
            "description": "Hochwertige Textil-Box mit verstärktem Boden und eleganten Details. Passt in jeden Wohnstil.",
            "price": 44.99,
            "stock": 50,
            "category_id": categories[2].id,
            "image_url": "/static/images/baskets_002.png"
        },
        # Sets & Bundles
        {
            "name": "OWRE Premium Set 4-teilig",
            "description": "Komplettes 4-teiliges Set mit verschiedenen Größen für komplette Raum-Organisation. Perfekt zum Sparen!",
            "price": 129.99,
            "stock": 25,
            "category_id": categories[3].id,
            "image_url": "/static/images/room_001.png"
        },
        {
            "name": "OWRE Family Bundle 6-teilig",
            "description": "Großes Bundle mit 6 Aufbewahrungsboxen in verschiedenen Größen und Farben. Ideal für Familien.",
            "price": 189.99,
            "stock": 15,
            "category_id": categories[3].id,
            "image_url": "/static/images/room_002.png"
        },
        # Zubehör
        {
            "name": "OWRE Griffe Premium Set",
            "description": "Ersatz- und zusätzliche hochwertige Griffe. Kompatibel mit allen OWRE Boxen.",
            "price": 14.99,
            "stock": 200,
            "category_id": categories[4].id,
            "image_url": "/static/images/baskets_003.png"
        },
        {
            "name": "OWRE Etiketten & Beschriftung",
            "description": "Elegante Etiketten zur Beschriftung Ihrer OWRE Boxen. 50er Set in verschiedenen Designs.",
            "price": 9.99,
            "stock": 300,
            "category_id": categories[4].id,
            "image_url": "/static/images/baskets_001.png"
        },
    ]
    
    for product_data in products_data:
        product = models.Product(**product_data)
        db.add(product)
    db.flush()
    
    # Create admin user for OWRE
    admin_user = models.User(
        email="admin@owre.shop",
        username="admin",
        firstname="Admin",
        lastname="OWRE",
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
        email="demo@owre.shop",
        username="demo",
        firstname="Demo",
        lastname="Kunde",
        phone="+49 (0) 123 456789",
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
        street="Musterstraße 123",
        city="Berlin",
        postal_code="10115",
        country="Deutschland",
        is_default=True
    )
    db.add(demo_address)
    
    db.commit()
    
    return {
        "detail": "OWRE Database initialized successfully",
        "categories_created": len(categories_data),
        "products_created": len(products_data),
        "admin_user": "admin@owre.shop (Password: admin123)",
        "demo_user": "demo@owre.shop (Password: demo123)"
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
