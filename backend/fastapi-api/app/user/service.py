from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Session

from app.user.models import User
from app.security import hash_password


class UserAlreadyExistsException(Exception):
    """Replaces UserAlreadyExistsException.java."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Replaces UserRepository.findById + UserService.findById."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Replaces UserRepository.findByUsername + UserService.findByUsername."""
    return db.query(User).filter(User.username == username).first()


def get_all_users(db: Session) -> list[User]:
    """Replaces UserRepository.findAll + UserService.findAll."""
    return db.query(User).all()


def create_user(db: Session, username: str, email: str, password: str) -> User:
    """
    Replaces UserService.createUser (business logic + @Transactional).
    Validates uniqueness and hashes the password before persisting.
    """
    if db.query(User).filter(User.username == username).first():
        raise UserAlreadyExistsException("Username already exists")

    if db.query(User).filter(User.email == email).first():
        raise UserAlreadyExistsException("Email already exists")

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
