from fastapi import FastAPI #type:ignore
from database import Base, engine
import user
import product
import cart
import order
import admin

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(admin.router)
