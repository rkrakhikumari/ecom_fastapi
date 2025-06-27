from pydantic import BaseModel, Field

class CreateUser(BaseModel):
    name : str = Field(min_length=3)
    email : str
    address : str
    password : str
    phone_number : str 
    role : str = Field(default='customer')


class VerifyOtp(BaseModel):
    email : str
    otp : str


class UserLogin(BaseModel):
    email : str
    password : str


class CreateProduct(BaseModel):
    name : str
    category : str
    price : float
    stock : str
    image_url : str


class UpdateProduct(BaseModel):
    name : str =None
    category : str =None
    price : float = None
    stock : str = None
    image_url : str = None



class AddToCart(BaseModel):
    product_id : int
    quantity : int = 1