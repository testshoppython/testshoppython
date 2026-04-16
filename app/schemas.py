from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        orm_mode = True

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    category_id: int
    stock: int = 0
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    created_at: datetime
    category: Optional[Category] = None
    class Config:
        orm_mode = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None

# Address Schemas
class AddressBase(BaseModel):
    street: str
    city: str
    postal_code: str
    country: str
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class Address(AddressBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    firstname: str
    lastname: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    phone: Optional[str] = None
    
class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    class Config:
        orm_mode = True

class UserWithAddresses(User):
    addresses: List[Address] = []

# Cart Item Schemas
class CartItemBase(BaseModel):
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    cart_id: int
    class Config:
        orm_mode = True

class CartItemWithProduct(CartItem):
    product: Product

# Cart Schemas
class CartBase(BaseModel):
    pass

class Cart(CartBase):
    id: int
    user_id: int
    items: List[CartItemWithProduct] = []
    class Config:
        orm_mode = True

# Order Item Schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    class Config:
        orm_mode = True

class OrderItemWithProduct(OrderItem):
    product: Product

# Order Schemas
class OrderBase(BaseModel):
    payment_method: str

class OrderCreate(OrderBase):
    items: Optional[List[CartItemBase]] = None
    shipping_address_id: Optional[int] = None
    promo_code: Optional[str] = None

class Order(OrderBase):
    id: int
    user_id: int
    order_number: str
    total_price: float
    discount_amount: float = 0.0
    promo_code: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemWithProduct] = []
    class Config:
        orm_mode = True
# Order Update Schema
class OrderUpdate(BaseModel):
    status: str

# Newsletter
class NewsletterSubscribeRequest(BaseModel):
    email: EmailStr
    interests: Optional[List[str]] = []