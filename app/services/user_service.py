from sqlalchemy.orm import Session
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def update_user(self, user, user_data: UserUpdate):
        update_data = user_data.dict(exclude_unset=True)
        return self.user_repo.update(user, update_data)