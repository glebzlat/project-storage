from fastapi import APIRouter


router = APIRouter()


@router.get("/healthcheck")
def healthcheck():
    return {"message": "The API is alive"}
