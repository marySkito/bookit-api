from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.service import Service
from ..schemas.service import ServiceCreate, ServiceUpdate

class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, service_data: ServiceCreate) -> Service:
        service = Service(**service_data.dict())
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service

    def get_all(self, q: str = None, price_min: float = None, 
                price_max: float = None, active: bool = None):
        query = self.db.query(Service)
        
        if active is not None:
            query = query.filter(Service.is_active == active)
        if q:
            query = query.filter(Service.title.contains(q))
        if price_min is not None:
            query = query.filter(Service.price >= price_min)
        if price_max is not None:
            query = query.filter(Service.price <= price_max)
            
        return query.all()

    def get_by_id(self, service_id: int) -> Service | None:
        return self.db.query(Service).filter(Service.id == service_id).first()

    def update(self, service: Service, update_data: ServiceUpdate) -> Service:
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(service, field, value)
        self.db.commit()
        self.db.refresh(service)
        return service

    def delete(self, service: Service):
        self.db.delete(service)
        self.db.commit()