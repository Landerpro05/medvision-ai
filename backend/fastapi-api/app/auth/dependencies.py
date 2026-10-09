from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.jwt import decode_access_token
from app.user.models import User
from app.user.service import get_user_by_id

# El esquema "Bearer" estándar para Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/swagger_login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Decodifica el JWT, verifica su validez y recupera el usuario asociado.
    Falla con 401 si el token es inválido o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
        
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
        
    if not user.enabled:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Verifica que el usuario actual tenga el rol ADMIN.
    """
    roles = [role.name for role in current_user.roles]
    if "ADMIN" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
