from sqlalchemy import  Column, Integer, String, VARCHAR, DECIMAL, TIMESTAMP, ForeignKey, Boolean
from shared.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Product(Base):

    __tablename__ = 'pims'
    id = Column(Integer, primary_key=True, index=True)       
    name = Column(VARCHAR(255))         
    description = Column(String, nullable =False)                    
    price =  Column(DECIMAL(10, 2), nullable= False)      
    stock = Column(Integer, default=0)
    category  = Column(VARCHAR(100))             
    image_url =  Column(VARCHAR(255))
    is_sold= Column(Boolean, default=False)
    created_at =  Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))  # ForeignKey to Users table
    owner = relationship("Users", back_populates="items")  # Establish relationship


