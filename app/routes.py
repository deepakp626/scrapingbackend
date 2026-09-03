from fastapi import APIRouter
from app.api import blogRoute
from app.api import pdfRoute




router = APIRouter()

# blog routes
router.include_router(blogRoute.router,tags=["blogs"])
# pdf routes
router.include_router(pdfRoute.router,tags=["PDF Tools"])

