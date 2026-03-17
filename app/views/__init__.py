from fastapi import APIRouter

from app.views.usuario import router as usuario
from app.views.propriedade_intelectual import router as propriedade_intelectual
from app.views.interesse import router as interesse
from app.views.dev_router import router as dev_router
from app.views.entidade import router as entidades
from app.views.laboratorio import router as laboratorios
from app.views.email import router as email

router = APIRouter()
router.include_router(usuario)
router.include_router(propriedade_intelectual)
router.include_router(interesse)
router.include_router(dev_router)
router.include_router(entidades)
router.include_router(laboratorios)
router.include_router(email)