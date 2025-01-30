from fastapi import FastAPI
from Product.model.routes import router as pro_router
from  Users.model.routes import router as u_router 
from shared.database import Base, engine
from Users.model.auth import router as auth_router

app = FastAPI()

app.include_router(pro_router)
app.include_router(u_router)
app.include_router(auth_router)

Base.metadata.create_all(engine)