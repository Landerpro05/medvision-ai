import uuid

from sqlalchemy import Column, String, Boolean, TypeDecorator, CHAR, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

class UUIDType(TypeDecorator):
    """
    Tipo UUID compatible con PostgreSQL y SQLite.
    En PostgreSQL usa el tipo nativo UUID.
    En SQLite almacena como CHAR(32).
    """

    impl = CHAR(32)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value if isinstance(value, uuid.UUID) else uuid.UUID(value)
        else:
            if isinstance(value, uuid.UUID):
                return value.hex
            return uuid.UUID(value).hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        return value


from app.database import Base


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", UUIDType(), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class Role(Base):
    """
    Modelo SQLAlchemy para la tabla 'roles'.
    """

    __tablename__ = "roles"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)


class User(Base):
    """
    Modelo SQLAlchemy para la tabla 'users'.
    Compatible con PostgreSQL (producción) y SQLite (tests).
    """

    __tablename__ = "users"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)

    roles = relationship("Role", secondary=user_roles, lazy="joined")
