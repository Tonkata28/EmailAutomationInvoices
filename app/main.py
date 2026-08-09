from fastapi import FastAPI, Request

from routers import emails


app = FastAPI()
app.include_router(emails.router)

port = 8000

# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     # print(await request.json())
#     return await call_next(request)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)