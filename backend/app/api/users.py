from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserDTO, LearnerProfileDTO
from app.repositories.user_repo import UserRepository
from app.api.deps import get_db, get_current_user_id

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=dict)
async def get_me(user_id: str = Depends(get_current_user_id), session: AsyncSession = Depends(get_db)):
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Lazy loading relationship manually or we can eagerly load in repo. 
    # For now, since profile is related, we would await loading or change get_by_id to eager load it.
    # To keep it simple, let's just return what we have mapped for now.
    
    return {
        "user": {
            "id": str(user.id),
            "name": user.full_name,
            "email": user.email,
        }
    }
