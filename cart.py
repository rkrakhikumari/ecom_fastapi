from fastapi import APIRouter, Depends, HTTPException
from user import db_dependency
from schemas import AddToCart
from user import get_customer
from models import Product, CartItem, Order

router = APIRouter(
    prefix = '/cart',
    tags = ['cart and checkout']


)

@router.post('/add-to-cart')
def add_to_cart(item: AddToCart, db: db_dependency, user_data: dict = Depends(get_customer)):
    product = db.query(Product).filter(Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')

    if item.quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot add {item.quantity} units. Only {product.stock} units in stock."
        )

    existing_cart_item = db.query(CartItem).filter(
        CartItem.user_id == user_data['user'].id,
        CartItem.product_id == item.product_id
    ).first()

    if existing_cart_item:
        total_quantity = existing_cart_item.quantity + item.quantity
        if total_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Total quantity in cart would exceed stock. Available: {product.stock}, Already in cart: {existing_cart_item.quantity}"
            )
        existing_cart_item.quantity += item.quantity
        db.commit()
        return {'msg': 'Updated quantity in cart', 'product_name': product.name}

    cart_item = CartItem(
        user_id=user_data['user'].id,
        product_id=item.product_id,
        quantity=item.quantity
    )

    db.add(cart_item)
    db.commit()
    return {'msg': 'Added to cart', 'product_name': product.name}


@router.get('/view-cart')
def view_cart(db: db_dependency, user_data : dict = Depends(get_customer)):
    items = db.query(CartItem).filter(CartItem.user_id == user_data['user'].id).all()
    cart =[]
    total = 0
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product_total = product.price * item.quantity
            cart.append(
                {'product': product.name,
                'quantity': item.quantity,
                'price': product.price,
                'total': product_total


            }
            
            )
            total += product_total


    return {'cart': cart, 'total': total}



@router.delete('/remove-item/{item_id}')
def remove_cart_item(item_id: int, db: db_dependency, user_data : dict= Depends(get_customer)):
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user_data['user'].id).first()
    if not item:
        raise HTTPException(status_code=404, detail= 'item not found')
    
    db.delete(item)

    db.commit()

    return {'msg':'item removed sucessfully',}



@router.post('/checkout')
def checkout(db: db_dependency, user_data : dict = Depends(get_customer)):
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_data["user"].id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail='no item in cart')
    
    total_sum = 0
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            total_sum += product.price * item.quantity


    new_order = Order(user_id = user_data['user'].id, total_amount = total_sum, status = 'completed')
    db.add(new_order)

    for item in cart_items:
        db.delete(item)
    
    db.commit()
    return {'msg':'order placed successfully', 'total_amount': total_sum}

    




