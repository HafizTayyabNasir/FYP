from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User as UserSchema
from app.schemas.auth import Token, AuthResponse, Login
from app.services.email.verification import send_verification_email

router = APIRouter()

@router.post("/signup", response_model=dict)
async def signup(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Create new user
    token = security.generate_verification_token()
    token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=security.get_password_hash(user_in.password),
        verification_token=token,
        token_expires_at=token_expires_at,
        is_verified=False,
        is_active=True,
        role="user",
        plan="none"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Send verification email
    # Determine frontend URL
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
    send_verification_email(user.email, token, frontend_url)
    
    return {"message": "User registered successfully. Please check your email to verify."}

@router.post("/login", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Find user
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    # Verify
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    elif not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")
        
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return {
        "token": access_token,
        "user": UserSchema.model_validate(user)
    }

@router.post("/login/json", response_model=AuthResponse)
async def login_json(
    login_data: Login,
    db: AsyncSession = Depends(get_db)
) -> Any:
    # Find user
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalars().first()
    
    # Verify
    if not user or not security.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    elif not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")
        
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    
    return {
        "token": access_token,
        "user": UserSchema.model_validate(user)
    }

@router.get("/verify-email", response_model=dict)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(User).where(User.verification_token == token))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
        
    if user.token_expires_at and user.token_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expired")
        
    user.is_verified = True
    user.verification_token = None
    user.token_expires_at = None
    await db.commit()
    
    return {"message": "Email verified successfully"}

@router.get("/me", response_model=UserSchema)
async def get_current_user(
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    return UserSchema.model_validate(current_user)

@router.post("/select-plan", response_model=UserSchema)
async def select_plan(
    plan: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    if plan not in ["individual", "team"]:
        raise HTTPException(status_code=400, detail="Invalid plan")
        
    current_user.plan = plan
    current_user.plan_started_at = datetime.now(timezone.utc)
    
    if plan == "individual":
        current_user.plan_expires_at = datetime.now(timezone.utc) + timedelta(days=90)
    elif plan == "team":
        current_user.plan_expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        
    await db.commit()
    await db.refresh(current_user)
    
    return UserSchema.model_validate(current_user)

