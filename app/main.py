from fastapi import FastAPI

app = FastAPI(title="Auth Service")

@app.get("/v1/health")
async def health():
    return {"status": "ok"}
