from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from base import get_db
from sqlalchemy import select, insert, update, delete
from models.task import Task, TaskStatus
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

notFoundResponseFormat = {
    "description": "Not Found",
    "content": {
        "application/json": {
            "example": {
                "detail": "Задача не найдена"
            }
        }
    }
}

@app.get(
    "/tasks/",
    summary="Получить задачи", 
    description="Получить задачи (с опциональным фильтром по статусу)",
)
async def get_tasks(status: TaskStatus = Query(None), db: AsyncSession = Depends(get_db)):
    query = select(Task)
    if status:
        query = query.where(Task.status == status)

    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks

@app.post(
    "/tasks/", 
    summary="Cоздать задачу", 
    description="Создать новую задачу",
)
async def create_task(title: str, status: TaskStatus, description = None, db: AsyncSession = Depends(get_db)):
    task = Task(title=title, description=description, status=status)
    db.add(task)

    await db.commit()
    await db.refresh(task)

    return {"id": task.id, "title": task.title, "description": task.description, "status": task.status}

@app.put(
    "/tasks/{task_id}/", 
    summary="Изменить задачу", 
    description="Изменить название/статус/описание задачи по ID, если она существует",
    responses={
        404: notFoundResponseFormat,
    }    
)
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

@app.delete(
    "/tasks/{task_id}/",
    summary="Удалить задачу", 
    description="Удалить задачу по ID, если она существует",
    responses={
        404: notFoundResponseFormat,
    }
)
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
