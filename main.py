from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import emails, info
from app.middleware.logging import log_request
from app.data.data import db
from app.services.gmail import load_history_id
from app.config import Settings


app = FastAPI()

# API routers
# app.include_router(emails.router)
app.include_router(info.router)


app.middleware("http")(log_request)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# db["last_history_id"] = load_history_id() # make this the last resort, always load just the latest edited history id and not just reset on restart


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)

    print(db["last_history_id"])


