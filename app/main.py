from fastapi import FastAPI
from base import database
from models.task import Task

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/tasks/")
async def get_tasks():
    query = Task.__table__.select()
    users = await database.fetch_all(query)
    return users

# @app.post("/users/")
# async def create_user(name: str, email: str):
#     query = User.__table__.insert().values(name=name, email=email)
#     user_id = await database.execute(query)
#     return {"id": user_id, "name": name, "email": email}

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
