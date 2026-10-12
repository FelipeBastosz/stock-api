from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth import service
from src.modules.auth.dependencies import get_current_user
from src.modules.auth.models import User
from src.modules.auth.schemas import (
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário",
    description="Cria um novo usuário com papel de administrador ou operador.",
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_user(db, payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Autenticar e obter token JWT",
    description="Autentica com credenciais e retorna o token de acesso (suporta OAuth2 e formulário Swagger).",
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    return await service.login_user(db, form_data.username, form_data.password)


@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Autenticar via JSON e obter JWT",
    description="Endpoint alternativo que aceita JSON no corpo da requisição.",
)
async def login_json(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.login_user(db, payload.username, payload.password)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Perfil do usuário atual",
    description="Retorna informações do usuário autenticado a partir do token JWT.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user
