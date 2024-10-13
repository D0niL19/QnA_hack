from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from fastapi_server.router import router
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # "http://localhost:3000",
        # "http://localhost",
        "http://176.123.163.187:3000",
        "http://176.123.163.187",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Разрешенные методы
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=8080)
