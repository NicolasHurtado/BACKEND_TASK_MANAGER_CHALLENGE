"""
Task management endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import ActiveUserDep, TaskRepositoryDep
from app.models.task import Task, TaskCreate, TaskStats, TaskStatus, TaskUpdate

router = APIRouter()


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreate,
    current_user: ActiveUserDep,
    task_repo: TaskRepositoryDep
) -> Task:
    """
    Crear una nueva tarea
    """
    task_in_db = await task_repo.create_task(task_create, str(current_user.id))
    return task_repo.to_public_task(task_in_db)


@router.get("/", response_model=List[Task])
async def get_user_tasks(
    current_user: ActiveUserDep,
    task_repo: TaskRepositoryDep,
    status: Optional[TaskStatus] = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0, description="Número de tareas a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de tareas a retornar")
) -> List[Task]:
    """
    Obtener todas las tareas del usuario actual con filtros opcionales
    """
    tasks = await task_repo.get_user_tasks(
        str(current_user.id),
        status=status,
        skip=skip,
        limit=limit
    )
    return [task_repo.to_public_task(task) for task in tasks]


@router.get("/stats", response_model=TaskStats)
async def get_task_statistics(
    current_user: ActiveUserDep,
    task_repo: TaskRepositoryDep
) -> TaskStats:
    """
    Obtener estadísticas de tareas del usuario actual
    """
    return await task_repo.get_user_task_stats(str(current_user.id))


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    current_user: ActiveUserDep,
    task_repo: TaskRepositoryDep
) -> Task:
    """
    Obtener una tarea específica por ID
    """
    task = await task_repo.get_task_by_id(task_id, str(current_user.id))
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    return task_repo.to_public_task(task)


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    current_user: ActiveUserDep,
    task_repo: TaskRepositoryDep
) -> Task:
    """
    Actualizar una tarea específica
    """
    updated_task = await task_repo.update_task(
        task_id, 
        task_update, 
        str(current_user.id)
    )
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    return task_repo.to_public_task(updated_task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: ActiveUserDep,
    task_repo: TaskRepositoryDep
) -> None:
    """
    Eliminar una tarea específica
    """
    success = await task_repo.delete_task(task_id, str(current_user.id))
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )


# Endpoints adicionales para funcionalidades específicas
@router.patch("/{task_id}/status", response_model=Task)
async def update_task_status(
    task_id: str,
    new_status: TaskStatus,
    current_user: ActiveUserDep,
    task_repo: TaskRepositoryDep
) -> Task:
    """
    Actualizar solo el estado de una tarea
    """
    task_update = TaskUpdate(status=new_status)
    updated_task = await task_repo.update_task(
        task_id, 
        task_update, 
        str(current_user.id)
    )
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarea no encontrada"
        )
    return task_repo.to_public_task(updated_task)


@router.get("/status/{status}", response_model=List[Task])
async def get_tasks_by_status(
    status: TaskStatus,
    current_user: ActiveUserDep,
    task_repo: TaskRepositoryDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> List[Task]:
    """
    Obtener tareas por estado específico
    """
    tasks = await task_repo.get_user_tasks(
        str(current_user.id),
        status=status,
        skip=skip,
        limit=limit
    )
    return [task_repo.to_public_task(task) for task in tasks] 