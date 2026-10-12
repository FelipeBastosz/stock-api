from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictException, UnauthorizedException
from src.core.security import create_access_token, hash_password, verify_password
from src.modules.auth.models import User
from src.modules.auth.schemas import TokenResponse, UserCreate


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    username_clean = data.username.strip()
    stmt_user = select(User).where(func.lower(User.username) == username_clean.lower())
    if (await db.execute(stmt_user)).scalar_one_or_none():
        raise ConflictException("Nome de usuário já cadastrado.")

    email_clean = str(data.email).lower().strip()
    stmt_email = select(User).where(func.lower(User.email) == email_clean)
    if (await db.execute(stmt_email)).scalar_one_or_none():
        raise ConflictException("Email já cadastrado.")

    hashed = hash_password(data.password)
    user = User(
        username=username_clean,
        email=email_clean,
        hashed_password=hashed,
        role=data.role.value if hasattr(data.role, "value") else str(data.role),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User:
    stmt = select(User).where(func.lower(User.username) == username.strip().lower())
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedException("Usuário ou senha incorretos.")

    if not user.is_active:
        raise UnauthorizedException("Conta de usuário inativa.")

    return user


async def login_user(db: AsyncSession, username: str, password: str) -> TokenResponse:
    user = await authenticate_user(db, username, password)
    token = create_access_token({"sub": user.username, "role": user.role, "id": user.id})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        username=user.username,
    )
