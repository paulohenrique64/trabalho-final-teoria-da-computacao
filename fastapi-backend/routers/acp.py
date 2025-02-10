
# Automato com pilha

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_afd():
    return {"message": " ACP endpoint is working"}

