from fastapi import APIRouter

router = APIRouter(prefix="/team", tags=["Team"])

#Endpoint de prueba
@router.get("/")
async def hello_router():
    return {"Hello": "Teams!"}
