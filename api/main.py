from fastapi import FastAPI, Depends

from api.routes.health_check import HealthCheck

app = FastAPI(title="Youtube Research API")

@app.get("/")
def root():
    return { "message" : "app is running"}



@app.get("/health")
def health():
    return HealthCheck.execute()

