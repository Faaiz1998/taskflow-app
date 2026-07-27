import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import engine, get_db, Base
from app import models, schemas

# Creates tables on startup if they don't exist yet.
# Fine for week 0 local dev; you'd normally replace this with a proper
# migration tool (Alembic) before calling anything "production," but
# that's out of scope for this project's learning goals.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(title=task.title)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks", response_model=list[schemas.TaskOut])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).order_by(models.Task.created_at.desc()).all()


@app.patch("/tasks/{task_id}/complete", response_model=schemas.TaskOut)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.is_complete = True
    db_task.completed_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(db_task)
    return db_task
