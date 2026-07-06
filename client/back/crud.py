import random
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from typing import Dict
from client.back.database import Order, OrderItemTable
from client.back.models import OrderItemSchema
from client.back.redis_client import redis_client

async def get_order_with_items(db: AsyncSession, order_id: int) -> Order:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items), selectinload(Order.user))
    )
    return result.scalar_one_or_none()

async def create_order(db: AsyncSession, user_id: int, items: Dict[str, OrderItemSchema]) -> Order:
    
    rand_number = random.randint(100, 999)

    db_order = Order(user_id=user_id, status="новый", order_number=rand_number)
    db.add(db_order)
    await db.flush()
    
    for item_data in items.values():
        db_item = OrderItemTable(
            order_id=db_order.id,
            name=item_data.name,
            price=item_data.price,
            amount=item_data.amount
        )
        db.add(db_item)
    
    await db.commit()
    
    
    full_order = await get_order_with_items(db, db_order.id)
    
    
    try:
        order_data = {
            "username": full_order.user_name,
            "order_number": full_order.order_number,
            "status": full_order.status,
            "items": [
                {
                    "name": item.name,
                    "price": item.price,
                    "amount": item.amount
                }
                for item in full_order.items
            ],
            "created_at": full_order.created_at.isoformat()
        }
        redis_key = f"order:{full_order.order_number}"
        await redis_client.set(redis_key, json.dumps(order_data))
    except Exception as e:
        print(f"Failed to cache order to Redis: {e}")
        
    return full_order
