from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from user import get_db
from schemas import CreateOrder, UpdateOrderStatus, UpdatePaymentStatus
from sqlalchemy.orm import Session
from models import User, CartItem, Product, Order, OrderItem
from user import require_admin  , get_customer

router = APIRouter(
    prefix='/order',
    tags=['orders']


)

db_dependency = Annotated[Session, Depends(get_db)]



@router.post('/create-order')
def create_order(order_data: CreateOrder, db: db_dependency, current_user: dict = Depends(get_customer)):
    user = db.query(User).filter(User.id == order_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart_items = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total_amount = 0


    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.name}. Available: {product.stock}, Required: {item.quantity}")
        total_amount += product.price * item.quantity


    new_order = Order(
        user_id=user.id,
        total_amount=total_amount,
        status='pending',
        payment_status='pending'
    )
    db.add(new_order)
    db.commit()


    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock -= item.quantity  
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(order_item)

    db.query(CartItem).filter(CartItem.user_id == user.id).delete()
    db.commit()

    return {'order_id': new_order.id, 'msg': 'Order placed successfully'}



@router.get('/status/{order_id}')
def get_order_status(order_id: int, db: db_dependency):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "order_id": order.id,
        "order_status": order.status,
        "payment_status": order.payment_status,
        "total_amount": order.total_amount,

 
    }


@router.put('/update-status/{order_id}')
def order_update_status(order_id: int,status_data: UpdateOrderStatus,db: db_dependency,current_user: dict = Depends(require_admin)  ):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail='Order not found')

    order.status = status_data.status
    db.commit()
    return {'msg': f'Order status updated to {status_data.status}'}



@router.put('/payment-status/{order_id}')
def update_payment_status(order_id: int,payment_data: UpdatePaymentStatus,db: db_dependency,current_user: dict = Depends(require_admin)  ):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.payment_status = payment_data.payment_status
    db.commit()
    return {'msg': f'Payment status updated to {payment_data.payment_status}'}
