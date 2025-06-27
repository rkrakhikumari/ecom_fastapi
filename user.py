import random
from jose import jwt, JWTError#type:ignore
from fastapi import Depends , APIRouter, status, HTTPException #type:ignore
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext #type:ignore
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from schemas import UserLogin, CreateUser, VerifyOtp
from models import User
from fastapi.security import OAuth2PasswordBearer#type:ignore



SECRET_KEY = 'Zb3KzQJd5gqLi87hHtRHafcM_zkExrbTSo1xgcy-BSk'

ALGORITHM = 'HS256'

router = APIRouter(
    prefix='/user',
    tags = ['user']



)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="user/login")


def generate_otp():
    otp=str(random.randint(100000, 999999))
    otp_expiry = datetime.now() + timedelta(minutes=15)
    return otp, otp_expiry



def hased_paswrd(password: str):
    return pwd_context.hash(password)




def verify_paswrd(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()  
    expire = datetime.now(timezone.utc) + expires  
    to_encode.update({"exp": expire})  
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt 


def get_current_user(db: db_dependency, token: str=Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email : str = payload.get('sub')
        role : str = payload.get('role')
        if email is None or role is None:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not validate token")

    except JWTError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Could not validate token")

    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code = 404, detail="user not found")
    return {'user': user, 'role': role}


def get_vendor(current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'vendor':
        raise HTTPException(status_code = 403, detail = 'vendor access required')
    return current_user



def get_customer(current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'customer':
        raise HTTPException(status_code = 403, detail = 'customer access req')
    return current_user


def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get('/')
def get_all_users(db: db_dependency):
    users = db.query(User).all()
    if not users:
        raise HTTPException(status_code = 404, detail ='no user found')
    user_list = []
    for user in users:
        user_list.append(

            {"id":user.id,
    "name": user.name,
    "email":user.email,
    "address": user.address,
    "phone_number":user.phone_number,
    "password":user.password,
    "otp": user.otp,
    "otp_expiry": str(user.otp_expiry) if user.otp_expiry else None,
    "role": user.role,
    "is_verified":user.is_verified


            }

        )
    return {"users": user_list}



@router.post('/register', status_code = status.HTTP_201_CREATED)
def registration(user: CreateUser, db: db_dependency):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='email already register')
    otp, otp_expiry = generate_otp()


    new_user = User(
        name = user.name,
        email = user.email,
        address = user.address,
        phone_number=user.phone_number,
        password = hased_paswrd(user.password),
        otp = otp,
        otp_expiry=otp_expiry,
        role=user.role,
        is_verified = False



    )
    db.add(new_user)
    db.commit()
    return {'msg':'regitration done', 'otp': otp}


@router.post('/verify-otp')
def verify_otp(otp_is: VerifyOtp, db: db_dependency):
    user = db.query(User).filter(User.email == otp_is.email).first()
    if not user:
        raise HTTPException(status_code = 404, detail ='user not found')
    if user.otp != otp_is.otp:
        raise HTTPException(status_code =400, detail = 'wrong otp')
    
    user.is_verified = True
    db.commit()
    return {'msg':'otp verified'}



@router.post('/login', status_code = status.HTTP_200_OK)
def user_login(user: UserLogin, db: db_dependency):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_paswrd(user.password, db_user.password):
        raise HTTPException(status_code = 401, detail =' not valid username or password')
    token = create_access_token(data={'sub':db_user.email, 'role': db_user.role})
    return {'access_toke': token, 'type': 'bearer'}

    
    
@router.get('/all-vendors')
def get_all_vendors(user: dict = Depends(get_vendor)):
    return {'msg': f'hello vendor {user["user"].name}this is vendor data'}


@router.get('/all-customer')
def get_all_customer(user: dict = Depends(get_customer)):
    return {'msg':f'hello customer {user["user"].name} this is customer data'}


@router.get('/admin-only')
def admin_area(user: dict = Depends(require_admin)):
    return {'msg': f'Hello Admin {user["user"].name}, here is your admin data'}