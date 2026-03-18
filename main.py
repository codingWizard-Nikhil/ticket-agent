from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import engine
from app import models
from app.routes import router as tickets_router
from app.email_processor import process_emails

models.Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()
scheduler.add_job(process_emails, "interval", minutes=5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Ticket Agent", lifespan=lifespan)
app.include_router(tickets_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/process-emails")
def run_email_processor():
    return process_emails()
