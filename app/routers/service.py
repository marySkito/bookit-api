from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..dependencies import require_admin
from ..schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from ..services.service_service import ServiceService

router = APIRouter()

@router.get("/", response_model=list[ServiceResponse])
def get_services(
    q: Optional[str] = Query(None, description="Search query"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    service_service = ServiceService(db)
    return service_service.get_all_services(q, price_min, price_max, active)

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service_service = ServiceService(db)
    service = service_service.get_service_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )
    return service

@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service_data: ServiceCreate,
    admin_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    service_service = ServiceService(db)
    return service_service.create_service(service_data)

@router.patch("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    admin_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    service_service = ServiceService(db)
    return service_service.update_service(service_id, service_data)

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    admin_user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    service_service = ServiceService(db)
    service_service.delete_service(service_id)