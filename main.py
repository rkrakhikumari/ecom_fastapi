from fastapi import FastAPI #type:ignore
from database import Base, engine
import user


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(user.router)


