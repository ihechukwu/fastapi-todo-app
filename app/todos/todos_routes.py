from fastapi import APIRouter
from fastapi.responses import JSONResponse

todos_router = APIRouter()


@todos_router.get("/")
async def test():

    return JSONResponse(content={"msg": "working perfectly"})
