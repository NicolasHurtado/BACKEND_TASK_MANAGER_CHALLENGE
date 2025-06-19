"""
User management endpoints
"""

from typing import List

from fastapi import APIRouter, HTTPException, status

from app.core.deps import ActiveUserDep, UserRepositoryDep
from app.models.user import User, UserUpdate, PasswordChange
from app.core.security import verify_password, get_password_hash

router = APIRouter()


@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: ActiveUserDep,
    user_repo: UserRepositoryDep
) -> User:
    """
    Obtener perfil del usuario actual
    """
    return user_repo.to_public_user(current_user)


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: ActiveUserDep,
    user_repo: UserRepositoryDep
) -> User:
    """
    Actualizar información del usuario actual
    """
    try:
        updated_user = await user_repo.update_user(
            str(current_user.id), 
            user_update
        )
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return user_repo.to_public_user(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_change: PasswordChange,
    current_user: ActiveUserDep,
    user_repo: UserRepositoryDep
) -> None:
    """
    Cambiar contraseña del usuario actual
    """
    # Verify current password
    if not verify_password(password_change.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    
    # Hash new password
    new_hashed_password = get_password_hash(password_change.new_password)
    
    # Update password in database
    success = await user_repo.change_password(str(current_user.id), new_hashed_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al cambiar la contraseña"
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: ActiveUserDep,
    user_repo: UserRepositoryDep
) -> None:
    """
    Eliminar cuenta del usuario actual
    """
    success = await user_repo.delete_user(str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )


# Admin endpoints (opcional para futuras funcionalidades)
@router.get("/", response_model=List[User])
async def get_all_users(
    current_user: ActiveUserDep,
    user_repo: UserRepositoryDep,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    """
    Obtener todos los usuarios (funcionalidad de administrador)
    """
    # TODO: Add admin role check
    users = await user_repo.get_all_users(skip=skip, limit=limit)
    return [user_repo.to_public_user(user) for user in users]


@router.get("/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: str,
    current_user: ActiveUserDep,
    user_repo: UserRepositoryDep
) -> User:
    """
    Obtener usuario por ID (funcionalidad de administrador)
    """
    # TODO: Add admin role check or allow users to view their own profile
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user_repo.to_public_user(user) 