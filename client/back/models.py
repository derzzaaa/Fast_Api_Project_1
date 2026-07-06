from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class OrderItemSchema(BaseModel):
    name: str = Field(..., description="Название товара/напитка", min_length=1)
    price: float = Field(..., description="Цена за единицу товара", gt=0)
    amount: int = Field(..., description="Количество товара", gt=0)


class OrderItemResponse(BaseModel):
    id: int
    name: str
    price: float
    amount: int

    class Config:
        from_attributes = True

class OrderResponseSchema(BaseModel):
    id: int
    order_number: int
    user_name: str
    status: str
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True



class UserRegisterSchema(BaseModel):
    login: str = Field(..., description="Логин", min_length=3, max_length=50)
    username: str = Field(..., description="Имя пользователя для отображения", min_length=3, max_length=50)
    password: str = Field(..., description="Пароль", min_length=6)

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class UserResponseSchema(BaseModel):
    login: str
    username: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None

    class Config:
        from_attributes = True

class UserUpdateSchema(BaseModel):
    login: str = Field(..., description="Логин", min_length=3, max_length=50)
    username: str = Field(..., description="Имя пользователя для отображения", min_length=3, max_length=50)
    password: str = Field(None, description="Новый пароль (необязательно)", min_length=6)
