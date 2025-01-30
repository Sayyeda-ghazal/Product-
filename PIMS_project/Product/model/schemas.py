from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class product(BaseModel):
    name : str        
    description : str                  
    price :  int      
    stock : int
    category  : str             
    image_url :  Optional[str] = None
    created_at :  Optional[str] = None
    updated_at : Optional[str] = None
    is_sold: bool = False
    owner_id : Optional[int] = None
    class Config:
        form_attribute = True

class SaleSchema(BaseModel):
    name: str
    stock: int
    email : EmailStr

class filter_products(BaseModel):
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None








