from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def hello_router():
    return {"message":"Hello router!"}

