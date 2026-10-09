from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.user.service import get_user_by_email
from app.security import verify_password
from app.auth.jwt import create_access_token
from app.auth.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint para autenticación con esquema JSON.
    """
    user = get_user_by_email(db, request.email)
    
    # Prevención de ataques de enumeración (401 genérico)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    roles = [role.name for role in user.roles]
    access_token = create_access_token(subject=user.id, roles=roles)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/swagger_login")
def swagger_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint de login usado específicamente por Swagger UI (form data en vez de JSON).
    OAuth2PasswordBearer por defecto envía username/password en un form-data.
    Mapeamos 'username' al 'email' del usuario.
    """
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    roles = [role.name for role in user.roles]
    access_token = create_access_token(subject=user.id, roles=roles)
    
    return {"access_token": access_token, "token_type": "bearer"}
