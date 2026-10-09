import jwt
from datetime import datetime, timedelta, timezone
from typing import Any

from app.config import get_settings

settings = get_settings()


def create_access_token(subject: str | Any, roles: list[str]) -> str:
    """
    Crea un JWT de acceso con el subject (normalmente user_id) y los roles.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "roles": roles,
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    Decodifica un JWT y verifica su validez y expiración.
    Devuelve el payload si es válido, None en caso contrario.
    """
    try:
        decoded_token = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return decoded_token
    except jwt.PyJWTError:
        return None
