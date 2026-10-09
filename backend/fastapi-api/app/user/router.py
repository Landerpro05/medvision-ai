from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.user.schemas import UserCreateRequest, UserResponse
from app.user.models import User
from app.auth.dependencies import require_admin, get_current_user
from app.user.service import (
    get_all_users,
    get_user_by_id,
    create_user,
    UserAlreadyExistsException,
)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
def find_all(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    """
    GET /api/users
    Solo accesible por administradores.
    Replaces UserController.findAll().
    """
    return get_all_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def find_by_id(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    GET /api/users/{id}
    Un usuario solo puede consultar su propia información, salvo que sea ADMIN.
    Replaces UserController.findById().
    """
    roles = [role.name for role in current_user.roles]
    if current_user.id != user_id and "ADMIN" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own profile",
        )
        
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create(request: UserCreateRequest, db: Session = Depends(get_db)):
    """
    POST /api/users
    Replaces UserController.createUser().
    """
    try:
        user = create_user(db, request.username, request.email, request.password)
        return user
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )
