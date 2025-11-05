from fastapi import FastAPI, Query, HTTPException
from base import database
from sqlalchemy import select, insert, update, delete
from models.task import Task, TaskStatus

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/tasks/")
async def get_tasks(status: TaskStatus = Query(None)):
    query = select(Task)
    if status:
        query = query.where(Task.status == status)
    
    tasks = await database.fetch_all(query)
    return tasks

@app.post("/tasks/")
async def create_task(title: str, description: str, status: TaskStatus):
    query = insert(Task).values(title=title, description=description, status=status)
    task_id = await database.execute(query)
    return {"id": task_id, "title": title, "description": description, "status": status} 

@app.put("/tasks/{task_id}/")
async def update_task(task_id: int, title: str = None, description: str = None, status: TaskStatus = None):
    query = update(Task).where(Task.id == task_id)
    
    if title is not None:
        query = query.values(title=title)
    if description is not None:
        query = query.values(description=description)
    if status is not None:
        query = query.values(status=status)
    
    result = await database.execute(query)

    return result

@app.delete("/tasks/{task_id}/")
async def delete_task(task_id: int):
    query = delete(Task).where(Task.id == task_id)
    result = await database.execute(query)

    return result

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
