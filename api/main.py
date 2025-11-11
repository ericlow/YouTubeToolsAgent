from fastapi import FastAPI

app = FastAPI(title="Youtube Research API")

@app.get("/")
def root():
    return { "message" : "app is running"}

@app.get("/health")
def health():
    return { "message" : "OK"}