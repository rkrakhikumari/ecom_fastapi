from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from user import require_admin
from user import get_db
from models import User, Order, Product
from sqlalchemy import func


router = APIRouter(
    prefix= '/admin',
    tags=['Admin Dashboard']


)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get('/users')
def get_all_users(db: db_dependency, current_user: dict = Depends(require_admin)):
    users = db.query(User).all()  
    user_list = []

    for user in users:
        user_list.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "is_verified": user.is_verified
        }
        
        )

    return {"total_users": len(user_list), "users": user_list}



@router.get('/orders')
def get_all_orders(db: db_dependency, current_user: dict = Depends(require_admin)):
    orders = db.query(Order).all()
    order_list = []

    for order in orders:
        order_list.append({
            "order_id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "payment_status": order.payment_status,
            "total_amount": order.total_amount
        }
        
        
        )

    return {"total_orders": len(order_list), "orders": order_list}


@router.get('/sale-state')
def get_sale_state(db: db_dependency, current_user : dict = Depends(require_admin)):
    total_sales = db.query(Order).filter(Order.status.in_(["completed", "confirmed"])).count()
    total_revenue = db.query(func.sum(Order.total_amount)).filter(Order.status.in_(["completed", "confirmed"])).scalar()
    if total_revenue is None:
        total_revenue = 0  

    return {
        "total_completed_orders": total_sales,
        "total_revenue": total_revenue
    }



@router.get('/inventory')
def get_inventory(db: db_dependency, current_user : dict = Depends(require_admin)):
    products = db.query(Product).all()
    inventory_list = []
    for product in products:
        inventory_list.append({
            "product_id": product.id,
            "name": product.name,
            "stock": product.stock

        }
        
        )

    return {"total_products": len(inventory_list), "inventory": inventory_list}
