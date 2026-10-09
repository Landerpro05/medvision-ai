from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.user.models import User
from app.study.models import Study
from app.study.schemas import StudyCreate, StudyResponse

router = APIRouter(prefix="/api/studies", tags=["studies"])

@router.post("", response_model=StudyResponse, status_code=status.HTTP_201_CREATED)
def create_study(
    study_in: StudyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Crea un nuevo estudio asignado directamente al usuario autenticado.
    No permite que el cliente elija arbitrariamente el propietario.
    """
    study = Study(
        user_id=current_user.id,
        modality=study_in.modality,
        study_date=study_in.study_date,
        status="PENDING"
    )
    db.add(study)
    db.commit()
    db.refresh(study)
    return study


@router.get("", response_model=List[StudyResponse])
def get_my_studies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Devuelve la lista de estudios que pertenecen al usuario autenticado.
    """
    studies = db.query(Study).filter(Study.user_id == current_user.id).all()
    return studies


@router.get("/{study_id}", response_model=StudyResponse)
def get_study(
    study_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene los detalles de un estudio específico si pertenece al usuario.
    Si no existe o pertenece a otro usuario, devuelve 404 genérico 
    para no confirmar la existencia de estudios ajenos.
    """
    study = db.query(Study).filter(
        Study.id == study_id,
        Study.user_id == current_user.id
    ).first()
    
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study not found"
        )
        
    return study
