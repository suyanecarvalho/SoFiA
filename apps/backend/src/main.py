from fastapi import FastAPI

app = FastAPI(title="SofIA Backend")

@app.get("/")
def read_root():
    return {"message": "Welcome to the SofIA Financial AI Advisor API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok"}