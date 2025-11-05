from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from base import get_db
from sqlalchemy import select, insert, update, delete
from models.task import Task, TaskStatus

app = FastAPI()

@app.get("/tasks/")
async def get_tasks(status: TaskStatus = Query(None), db: AsyncSession = Depends(get_db)):
    query = select(Task)
    if status:
        query = query.where(Task.status == status)

    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks

@app.post("/tasks/")
async def create_task(title: str, status: TaskStatus, description = None, db: AsyncSession = Depends(get_db)):
    task = Task(title=title, description=description, status=status)
    db.add(task)

    await db.commit()
    await db.refresh(task)

    return {"id": task.id, "title": task.title, "description": task.description, "status": task.status}

@app.put("/tasks/{task_id}/")
async def update_task(task_id: int, title: str = None, status: TaskStatus = None, description: str = None, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if status is not None:
        task.status = status

    await db.commit()
    await db.refresh(task)

    return {"id": task.id, "title": task.title, "description": task.description, "status": task.status}

@app.delete("/tasks/{task_id}/")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    await db.delete(task)
    await db.commit()

    return {"detail": "Задача удаленна"}

@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
