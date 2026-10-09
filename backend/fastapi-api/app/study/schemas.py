from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class StudyBase(BaseModel):
    modality: Optional[str] = None
    study_date: Optional[datetime] = None

class StudyCreate(StudyBase):
    pass

class StudyResponse(StudyBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    
    # Configuración para compatibilidad con objetos SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
