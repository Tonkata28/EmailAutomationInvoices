import time
from fastapi import Request
import json

async def log_request(request: Request, call_next):

    # print(await request.body())
    # [print(f"{k}: {v}") for k, v in json.loads(await request.body()).items()]
    print()

    response = await call_next(request)

    print(response)

    return response