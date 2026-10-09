import uuid
from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base
from app.user.models import UUIDType

class Study(Base):
    """
    Modelo SQLAlchemy para la tabla 'studies'.
    Compatible con PostgreSQL y SQLite.
    """
    __tablename__ = "studies"

    id = Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUIDType(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Puede ser null hasta que no se suba la imagen real
    image_path = Column(String(500), nullable=True)
    
    # Nuevos campos de V3
    study_date = Column(DateTime, nullable=True)
    modality = Column(String(50), nullable=True)
    
    status = Column(String(30), nullable=False, default="PENDING")
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
