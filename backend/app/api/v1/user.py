"""用户相关API路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User
from app.schemas import BaseResponse, UserPermissionResponse, UserResponse
from app.services import PermissionService
from typing import List

router = APIRouter()


@router.get("/permissions", response_model=List[UserPermissionResponse])
def get_user_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户权限列表接口
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
    
    Returns:
        List[UserPermissionResponse]: 用户权限列表
    """
    permission_service = PermissionService(db)
    permissions = permission_service.get_user_permissions(current_user.id)
    return [UserPermissionResponse.model_validate(p) for p in permissions]


@router.get("/permissions/check")
def check_permission(
    permission_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """检查用户权限接口
    
    Args:
        permission_type: 权限类型
        current_user: 当前登录用户
        db: 数据库会话
    
    Returns:
        dict: 权限检查结果
    """
    permission_service = PermissionService(db)
    has_permission, message = permission_service.check_permission(
        current_user.id, permission_type, with_message=True
    )
    return {
        "has_permission": has_permission,
        "message": message
    }


@router.get("/profile", response_model=UserResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user)


@router.get("/balance")
def get_user_balance(
    current_user: User = Depends(get_current_user)
):
    """获取用户余额接口
    
    Args:
        current_user: 当前登录用户
    
    Returns:
        dict: 用户余额信息
    """
    return {
        "balance": float(current_user.balance)
    }
