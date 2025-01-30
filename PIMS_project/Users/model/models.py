from sqlalchemy import  Column, Integer, String, Enum
from shared.database import Base
from sqlalchemy.orm import relationship
from Users.model.schemas import Roles

class Users(Base):

    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    email = Column(String, unique=True, nullable=False)
    role = Column(Enum(Roles), default= "user")
    items = relationship("Product", back_populates="owner")  # Link to items
    



