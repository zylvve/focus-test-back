from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from base import get_db
from sqlalchemy import select, insert, update, delete
from models.task import Task, TaskStatus, TaskCreate, TaskUpdate
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
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    new_task = Task(title=task.title, description=task.description, status=task.status)
    db.add(new_task)

    await db.commit()
    await db.refresh(new_task)

    return {"id": new_task.id, "title": new_task.title, "description": new_task.description, "status": new_task.status}

@app.put(
    "/tasks/{task_id}/", 
    summary="Изменить задачу", 
    description="Изменить название/статус/описание задачи по ID, если она существует",
    responses={
        404: notFoundResponseFormat,
    }    
)
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    current_task = await db.get(Task, task_id)

    if not current_task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    if task.title is not None:
        current_task.title = task.title
    if task.description is not None:
        current_task.description = task.description
    if task.status is not None:
        current_task.status = task.status

    await db.commit()
    await db.refresh(current_task)

    return {"id": current_task.id, "title": current_task.title, "description": current_task.description, "status": current_task.status}

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
