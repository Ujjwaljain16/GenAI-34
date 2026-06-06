from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserLogin, AuthResponse
from app.services.auth import AuthService
from app.repositories.user_repo import UserRepository
from app.api.deps import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(session))

@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(data: UserCreate, service: AuthService = Depends(get_auth_service), session: AsyncSession = Depends(get_db)):
    result = await service.register(data)
    await session.commit()
    return result

@router.post("/login", response_model=AuthResponse)
async def login(data: UserLogin, service: AuthService = Depends(get_auth_service)):
    return await service.login(data)
