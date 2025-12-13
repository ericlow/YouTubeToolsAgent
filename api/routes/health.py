from fastapi import APIRouter

from api.routes.health_check import HealthCheck

router = APIRouter()

# HEALTH CHECK ENDPOINT
@router.get("/health")
def health():
    return HealthCheck.execute()
