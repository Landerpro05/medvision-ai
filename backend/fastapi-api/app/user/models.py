import uuid

from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class User(Base):
    """
    SQLAlchemy model – replaces the JPA @Entity User.java.
    Maps to the same 'users' table defined in V2__create_core_schema.sql.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
