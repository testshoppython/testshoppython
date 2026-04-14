from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .. import models, schemas

router = APIRouter(prefix="/users", tags=["Users"])

import bcrypt
import hashlib

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# bcrypt truncation fix: we manually SHA256 the password before bcrypt
# and use the raw bcrypt library to bypass passlib's buggy bug-detection.
def _get_safe_password(password: str) -> str:
    """Returns a SHA256 hex digest of the password for safe bcrypt hashing."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    # Use SHA256 digest as input to bcrypt
    hashed = bcrypt.hashpw(_get_safe_password(password), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # Try the new SHA256 pattern first
        safe_p = _get_safe_password(plain_password)
        h = hashed_password.encode('utf-8')
        if bcrypt.checkpw(safe_p, h):
            return True
    except:
        pass
    
    # Fallback for old plain-bcrypt entries if any
    try:
        return bcrypt.checkpw(plain_password[:72].encode('utf-8'), hashed_password.encode('utf-8'))
    except:
        return False

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(
        (models.User.email == user.email) | (models.User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email oder Username bereits registriert"
        )
    
    # Create new user
    hashed_password = hash_password(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        phone=user.phone,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create empty cart for user
    db_cart = models.Cart(user_id=db_user.id)
    db.add(db_cart)
    db.commit()
    
    return db_user

@router.get("/profile/{user_id}", response_model=schemas.UserWithAddresses)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User nicht gefunden"
        )
    return user

@router.put("/profile/{user_id}", response_model=schemas.User)
def update_user_profile(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User nicht gefunden"
        )
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/addresses", response_model=schemas.Address)
def add_address(user_id: int, address: schemas.AddressCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User nicht gefunden"
        )
    
    db_address = models.Address(
        user_id=user_id,
        street=address.street,
        city=address.city,
        postal_code=address.postal_code,
        country=address.country,
        is_default=address.is_default
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address

@router.get("/addresses/{user_id}", response_model=list[schemas.Address])
def get_user_addresses(user_id: int, db: Session = Depends(get_db)):
    addresses = db.query(models.Address).filter(models.Address.user_id == user_id).all()
    return addresses

@router.delete("/addresses/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db)):
    address = db.query(models.Address).filter(models.Address.id == address_id).first()
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adresse nicht gefunden"
        )
    
    db.delete(address)
    db.commit()
    return {"detail": "Adresse gelöscht"}
