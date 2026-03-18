from fastapi import FastAPI
from app.database import engine
from app import models
from app.routes import router as tickets_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ticket Agent")
app.include_router(tickets_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
