"""
Authentication endpoints
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.core.deps import UserRepositoryDep
from app.core.security import create_access_token, get_password_hash, verify_password, verify_token
from app.models.token import LoginResponse, RefreshTokenRequest, Token
from app.models.user import User, UserCreate, UserLogin

router = APIRouter()
settings = get_settings()


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    user_repo: UserRepositoryDep
) -> LoginResponse:
    """
    Registrar un nuevo usuario
    """
    # Check if user already exists
    existing_user = await user_repo.get_user_by_email(user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_create.password)
    
    try:
        user_in_db = await user_repo.create_user(user_create, hashed_password)
        
        # Create access token for the new user
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_in_db.email, "user_id": str(user_in_db.id)},
            expires_delta=access_token_expires
        )
        
        # Create refresh token (for now, same as access token)
        refresh_token = create_access_token(
            data={"sub": user_in_db.email, "user_id": str(user_in_db.id), "type": "refresh"},
            expires_delta=timedelta(days=7)  # Refresh tokens last longer
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user_repo.to_public_user(user_in_db).model_dump()
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
async def login_user(
    user_repo: UserRepositoryDep,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> LoginResponse:
    """
    Iniciar sesión y obtener token de acceso
    """
    # Authenticate user
    user = await user_repo.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=7)
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_repo.to_public_user(user).model_dump()
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    user_repo: UserRepositoryDep
) -> LoginResponse:
    """
    Renovar token de acceso usando refresh token
    """
    # Verify refresh token
    token_data = verify_token(refresh_request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de renovación inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await user_repo.get_user_by_email(token_data.email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    # Create new refresh token
    new_refresh_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=7)
    )
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        user=user_repo.to_public_user(user).model_dump()
    ) 