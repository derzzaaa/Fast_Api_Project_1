import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from client.back.database import Base, engine
from client.back.router import router as client_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


app.include_router(client_router)

app.mount("/", StaticFiles(directory="client/front", html=True), name="front")


if __name__ == "__main__":
    import os
    host = os.getenv("HOST", "127.0.0.1")
    reload = os.getenv("RELOAD", "false").lower() == "true"
    uvicorn.run("run_back:app", host=host, port=8000, reload=reload)
