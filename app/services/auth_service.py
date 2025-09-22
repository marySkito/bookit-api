from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from ..repositories.user_repository import UserRepository
from ..schemas.auth import UserRegister, UserLogin, Token
from ..utils.auth import get_password_hash, verify_password, create_access_token, create_refresh_token, verify_token
from ..config import settings

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, user_data: UserRegister):
        # Check if user already exists
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and create user
        password_hash = get_password_hash(user_data.password)
        user = self.user_repo.create(user_data, password_hash)
        return user

    def login_user(self, user_data: UserLogin) -> Token:
        # Authenticate user
        user = self.user_repo.get_by_email(user_data.email)
        if not user or not verify_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": user.email})
        
        return Token(access_token=access_token, refresh_token=refresh_token)

    def refresh_access_token(self, refresh_token: str) -> Token:
        payload = verify_token(refresh_token)
        
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        email = payload.get("sub")
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new tokens
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": user.email})
        
        return Token(access_token=access_token, refresh_token=new_refresh_token)