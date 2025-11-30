from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.dependencies import get_db

app = FastAPI(title="Youtube Research API")

@app.get("/")
def root():
    return { "message" : "app is running"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
#def health():

    try:
        db.execute(text("SELECT 1")).scalar()
        return {"message": "OK"}
    except Exception as e:
        return { "status": "ERROR", "error": str(e) }

