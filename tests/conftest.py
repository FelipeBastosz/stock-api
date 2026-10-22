import asyncio
from typing import AsyncGenerator
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.database import Base, get_db
from src.core.security import create_access_token, hash_password
from src.main import app
from src.modules.auth.models import User

# Import all models to ensure declarative metadata is complete
import src.modules.auth.models  # noqa: F401
import src.modules.categories.models  # noqa: F401
import src.modules.movements.models  # noqa: F401
import src.modules.products.models  # noqa: F401
import src.modules.suppliers.models  # noqa: F401

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    test_session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session: AsyncSession) -> User:
    admin = User(
        username="admin_test",
        email="admin_test@estoque.com",
        hashed_password=hash_password("admin_pass_123"),
        role="admin",
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest_asyncio.fixture(scope="function")
async def operator_user(db_session: AsyncSession) -> User:
    operator = User(
        username="operator_test",
        email="operator_test@estoque.com",
        hashed_password=hash_password("operator_pass_123"),
        role="operator",
        is_active=True,
    )
    db_session.add(operator)
    await db_session.commit()
    await db_session.refresh(operator)
    return operator


@pytest_asyncio.fixture(scope="function")
async def admin_headers(admin_user: User) -> dict:
    token = create_access_token({"sub": admin_user.username, "role": admin_user.role, "id": admin_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def operator_headers(operator_user: User) -> dict:
    token = create_access_token({"sub": operator_user.username, "role": operator_user.role, "id": operator_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture(scope="function")
async def auth_client(db_session: AsyncSession, admin_headers: dict) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=admin_headers) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def operator_client(db_session: AsyncSession, operator_headers: dict) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", headers=operator_headers) as ac:
        yield ac

    app.dependency_overrides.clear()
