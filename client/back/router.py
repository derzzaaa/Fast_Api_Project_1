from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from typing import Dict, List
from client.back.database import get_db, User, Order
from client.back.models import (
    OrderItemSchema, 
    OrderResponseSchema, 
    UserRegisterSchema, 
    TokenSchema, 
    UserResponseSchema,
    UserUpdateSchema
)
from client.back import crud
from client.back.auth import (
    get_current_user, 
    get_password_hash, 
    verify_password, 
    create_access_token
)

router = APIRouter(prefix="/api", tags=["Client Orders"])


@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterSchema,
    db: AsyncSession = Depends(get_db)
):

    login = payload.login.strip()
    username = payload.username.strip()
    
    username_check = await db.execute(select(User).where(User.username == username))
    if username_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
        
    login_check = await db.execute(select(User).where(User.login == login))
    if login_check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует"
        )
        
    hashed_password = get_password_hash(payload.password)
    new_user = User(
        login=login,
        username=username,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(User).where(User.username == form_data.username.strip()))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}




@router.post("/orders", response_model=OrderResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_new_order(
    payload: Dict[str, OrderItemSchema],  
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)  
):

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Заказ должен содержать хотя бы один товар"
        )

    try:
        
        db_order = await crud.create_order(db=db, user_id=current_user.id, items=payload)
        return db_order
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении заказа: {str(e)}"
        )


@router.get("/users/me", response_model=UserResponseSchema)
async def get_my_profile(current_user: User = Depends(get_current_user)):

    return current_user


@router.put("/users/me", response_model=UserResponseSchema)
async def update_profile(
    payload: UserUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    old_username = current_user.username
    new_username = payload.username.strip()
    new_login = payload.login.strip()
    
    if new_username != old_username:
        username_check = await db.execute(select(User).where(User.username == new_username))
        if username_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )
            
    if new_login != current_user.login:
        login_check = await db.execute(select(User).where(User.login == new_login))
        if login_check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким логином уже существует"
            )
        
    
    if payload.password:
        current_user.hashed_password = get_password_hash(payload.password)
        
    
    current_user.login = new_login
    current_user.username = new_username
    
    
    access_token = None
    token_type = None
    if new_username != old_username:
        access_token = create_access_token(data={"sub": new_username})
        token_type = "bearer"
    
    await db.commit()
    await db.refresh(current_user)
    
    response_data = {
        "login": current_user.login,
        "username": current_user.username,
        "access_token": access_token,
        "token_type": token_type
    }
    return response_data


@router.get("/orders/my", response_model=List[OrderResponseSchema])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    result = await db.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .options(selectinload(Order.items), selectinload(Order.user))
    )
    my_orders = result.scalars().all()
    return my_orders
