from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..repositories.service_repository import ServiceRepository
from ..schemas.service import ServiceCreate, ServiceUpdate

class ServiceService:
    def __init__(self, db: Session):
        self.db = db
        self.service_repo = ServiceRepository(db)

    def create_service(self, service_data: ServiceCreate):
        return self.service_repo.create(service_data)

    def get_all_services(self, q: str = None, price_min: float = None, 
                        price_max: float = None, active: bool = None):
        return self.service_repo.get_all(q, price_min, price_max, active)

    def get_service_by_id(self, service_id: int):
        return self.service_repo.get_by_id(service_id)

    def update_service(self, service_id: int, service_data: ServiceUpdate):
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        return self.service_repo.update(service, service_data)

    def delete_service(self, service_id: int):
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service not found"
            )
        self.service_repo.delete(service)