from fastapi import APIRouter
from app.api import blogRoute
from app.api import pdfRoute
from app.api import code_Engine_Route
from app.api import qr_Generate_Route




router = APIRouter()

# blog routes
router.include_router(blogRoute.router, prefix="/blogs", tags=["blogs"])
# pdf routes
router.include_router(pdfRoute.router, prefix="/pdf", tags=["PDF Tools"])
# Code execute route
router.include_router(code_Engine_Route.router, prefix="/code", tags=["Code Engine"])
# QR Code generation routes
router.include_router(qr_Generate_Route.router, prefix="/qr", tags=["QR Code"])
