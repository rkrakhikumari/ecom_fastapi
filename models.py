from sqlalchemy import Column, String, Integer, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from database import Base



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer,primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable= False)
    address = Column(String, nullable=False)
    is_verified = Column(Boolean, default= False)
    otp = Column(String)
    otp_expiry = Column(DateTime)
    role = Column(String, default='customer')


class Product(Base):
    __tablename__ ='products'
    id = Column(Integer, primary_key=True)
    category = Column(String, nullable= False)
    image_url = Column(String)
    price = Column(Float,nullable=False)
    stock = Column(String)
    vendor_id = Column(Integer, ForeignKey('users.id'))

    vendor = relationship("User")

