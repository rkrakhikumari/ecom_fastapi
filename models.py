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
    name = Column(String, nullable=False)
    category = Column(String, nullable= False)
    image_url = Column(String)
    price = Column(Float,nullable=False)
    stock = Column(Integer,nullable=False)
    vendor_id = Column(Integer, ForeignKey('users.id'))

    vendor = relationship("User")


class CartItem(Base):
    __tablename__='cartitem'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)

    product = relationship("Product")
    user = relationship("User")



class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(String, default='pending')
    total_amount = Column(Float, )
    payment_status = Column(String, default= 'pending')

    user = relationship("User")


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    order_id = Column(Integer, ForeignKey('orders.id'))
    quantity = Column(Integer, default=1)

    product = relationship("Product")

