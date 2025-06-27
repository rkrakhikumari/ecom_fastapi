from schemas import CreateProduct, UpdateProduct
from user import get_vendor, db_dependency
from fastapi import Depends, APIRouter, HTTPException
from models import Product


router = APIRouter(
    prefix = '/product',
    tags =['product']


)

@router.post('/create-product')
def create_product(product: CreateProduct, db: db_dependency, user_data : dict = Depends(get_vendor)):
    new_product = Product(
        name = product.name,
        category = product.category,
        price = product.price,
        stock = product.stock,
        image_url = product.image_url,
        vendor_id = user_data["user"].id,



    )
    db.add(new_product)
    db.commit()
    return {'msg':'product created', 'product_id': new_product.id}


@router.get('/all-product')
def get_all_product(db: db_dependency):
    products = db.query(Product).all()
    return products




@router.put('/update-product/{product_id}')
def update_product(product_id: int, update_prod : UpdateProduct, db:db_dependency, user_data : dict = Depends(get_vendor) ):
    product = db.query(Product).filter(Product.id == product_id, Product.vendor_id == user_data["user"].id).first()
    if not product:
        raise HTTPException(status_code=404, detail= 'product not found')
    product.name = update_prod.name
    product.category = update_prod.category
    product.price = update_prod.price
    product.stock = update_prod.stock

    db.commit()
    return {'msg':'product updated successfully'}



@router.delete('/delete-product/{product_id}')
def delete_product(product_id: int, db:db_dependency, user_data : dict = Depends(get_vendor) ):
    product = db.query(Product).filter(Product.id == product_id, Product.vendor_id == user_data["user"].id).first()
    if not product:
        raise HTTPException(status_code=404, detail='product not found')
    db.delete(product)
    db.commit()
    return {'msg':'product deleted', 'product_name': product.name}

    

