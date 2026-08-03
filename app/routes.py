from fastapi import APIRouter
from app.api import blogRoute




router = APIRouter()

# blog routes
router.include_router(blogRoute.router,tags=["blogs"])
