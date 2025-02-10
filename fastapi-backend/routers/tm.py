
# Maquina de turing

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_afd():
    return {"message": " TM endpoint is working"}

