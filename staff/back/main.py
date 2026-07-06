import asyncio
import json
import os
from dotenv import load_dotenv
import flet as ft
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from client.back.database import async_session, Order
from client.back.redis_client import redis_client
from staff.back.classes_controls import OrderCard, KanbanColumn

load_dotenv()

async def fetch_active_orders():
    
    async with async_session() as session:
        result = await session.execute(
            select(Order)
            .where(Order.status.in_(["новый", "готовится", "готов"]))
            .options(selectinload(Order.items), selectinload(Order.user))
            .order_by(Order.created_at.asc())  
        )
        return result.scalars().all()

async def update_order_status(order_id: int, new_status: str, order_number: int):
    
    async with async_session() as session:
        await session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(status=new_status)
        )
        await session.commit()
        
    
    redis_key = f"order:{order_number}"
    try:
        if new_status in ["выдан", "отменен"]:
            await redis_client.delete(redis_key)
        else:
            val = await redis_client.get(redis_key)
            if val:
                data = json.loads(val)
                data["status"] = new_status
                await redis_client.set(redis_key, json.dumps(data))
    except Exception as e:
        print(f"Ошибка при обновлении Redis для заказа {order_number}: {e}")

async def main(page: ft.Page):
    page.title = "Coffee & Bites — Панель Персонала"
    page.bgcolor = "#12100E"  
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    
    page.window_width = 1200
    page.window_height = 800
    page.window_min_width = 900
    page.window_min_height = 600
    
    
    logo_icon = ft.Icon(ft.Icons.COFFEE_ROUNDED, color="#D4A373", size=36)
    title_text = ft.Text(
        value="Coffee & Bites",
        color="#F5EBE6",
        size=24,
        weight=ft.FontWeight.BOLD,
    )
    subtitle = ft.Text(
        value="РАБОЧАЯ ДОСКА ЗАКАЗОВ (КУХНЯ / БАР)",
        color="#C2B2A9",
        size=10,
        weight=ft.FontWeight.W_600,
    )
    
    header_title_col = ft.Column(
        controls=[title_text, subtitle],
        spacing=0
    )
    
    header_left = ft.Row(
        controls=[logo_icon, header_title_col],
        spacing=12
    )
    
    
    new_count_txt = ft.Text("0", color="#FF9F1C", weight=ft.FontWeight.BOLD, size=16)
    prep_count_txt = ft.Text("0", color="#0496FF", weight=ft.FontWeight.BOLD, size=16)
    ready_count_txt = ft.Text("0", color="#2EC4B6", weight=ft.FontWeight.BOLD, size=16)
    
    stats_row = ft.Row(
        controls=[
            ft.Text("НОВЫЕ:", color="#C2B2A9", size=12, weight=ft.FontWeight.W_500),
            new_count_txt,
            ft.VerticalDivider(width=15, color="#4A3E39"),
            ft.Text("В РАБОТЕ:", color="#C2B2A9", size=12, weight=ft.FontWeight.W_500),
            prep_count_txt,
            ft.VerticalDivider(width=15, color="#4A3E39"),
            ft.Text("ГОТОВЫ:", color="#C2B2A9", size=12, weight=ft.FontWeight.W_500),
            ready_count_txt,
        ],
        spacing=8,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    stats_container = ft.Container(
        content=stats_row,
        bgcolor="#1A1715",
        padding=ft.Padding.symmetric(horizontal=20, vertical=10),
        border_radius=10,
        border=ft.Border.all(1, "#362E2A"),
    )
    
    
    refresh_btn = ft.IconButton(
        icon=ft.Icons.REFRESH_ROUNDED,
        icon_color="#D4A373",
        icon_size=28,
        tooltip="Обновить список заказов",
        on_click=lambda _: refresh_orders()
    )
    
    top_bar = ft.Row(
        controls=[
            header_left,
            stats_container,
            refresh_btn
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    
    col_new_items = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
    col_prep_items = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
    col_ready_items = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
    
    
    column_new = KanbanColumn("НОВЫЕ", "#FF9F1C", col_new_items)
    column_prep = KanbanColumn("ГОТОВЯТСЯ", "#0496FF", col_prep_items)
    column_ready = KanbanColumn("ГОТОВЫ К ВЫДАЧЕ", "#2EC4B6", col_ready_items)
    
    kanban_board = ft.Row(
        controls=[
            column_new,
            column_prep,
            column_ready
        ],
        spacing=15,
        expand=True
    )
    
    page.add(
        top_bar,
        ft.Divider(height=20, color="#2B2421"),
        kanban_board
    )
    
    updating = False
    
    async def handle_status_change(order_id: int, new_status: str, order_number: int):
        
        try:
            await update_order_status(order_id, new_status, order_number)
            
            status_labels = {
                "готовится": "перенесен в приготовление",
                "готов": "отмечен как готовый",
                "выдан": "выдан гостю",
                "отменен": "отменен"
            }
            label = status_labels.get(new_status, new_status)
            
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(
                        value=f"Заказ #{order_number} {label}",
                        color="#F5EBE6",
                        weight=ft.FontWeight.W_500
                    ),
                    bgcolor="#2B2421",
                    duration=3000
                )
            )
            await refresh_orders()
        except Exception as e:
            print(f"Ошибка изменения статуса заказа: {e}")
            
    async def handle_cancel(order_id: int, order_number: int):
        
        def close_dialog(e):
            page.dialog.open = False
            page.update()
            
        async def confirm_cancel(e):
            page.dialog.open = False
            page.update()
            await handle_status_change(order_id, "отменен", order_number)
            
        page.dialog = ft.AlertDialog(
            title=ft.Text("Подтверждение отмены", color="#F5EBE6"),
            content=ft.Text(f"Вы действительно хотите отменить заказ #{order_number}?", color="#C2B2A9"),
            bgcolor="#2B2421",
            actions=[
                ft.TextButton(
                    content=ft.Text("Да, отменить", color="#E76F51", weight=ft.FontWeight.BOLD),
                    on_click=confirm_cancel
                ),
                ft.TextButton(
                    content=ft.Text("Нет", color="#C2B2A9"),
                    on_click=close_dialog
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog.open = True
        page.update()
        
    async def refresh_orders():
        
        nonlocal updating
        if updating:
            return
        updating = True
        
        try:
            orders = await fetch_active_orders()
            print(f"DEBUG: Fetched {len(orders)} active orders from DB: {[(o.id, o.status, o.order_number) for o in orders]}")
            
            new_orders = [o for o in orders if o.status == "новый"]
            prep_orders = [o for o in orders if o.status == "готовится"]
            ready_orders = [o for o in orders if o.status == "готов"]
            print(f"DEBUG: new={len(new_orders)}, prep={len(prep_orders)}, ready={len(ready_orders)}")
            
            col_new_items.controls.clear()
            col_prep_items.controls.clear()
            col_ready_items.controls.clear()
            
            if new_orders:
                for o in new_orders:
                    col_new_items.controls.append(OrderCard(o, handle_status_change, handle_cancel))
            else:
                col_new_items.controls.append(
                    ft.Container(
                        content=ft.Text("Нет новых заказов", color="#C2B2A9", italic=True, size=14),
                        alignment=ft.Alignment(0, 0),
                        padding=20
                    )
                )
                
            if prep_orders:
                for o in prep_orders:
                    col_prep_items.controls.append(OrderCard(o, handle_status_change, handle_cancel))
            else:
                col_prep_items.controls.append(
                    ft.Container(
                        content=ft.Text("Нет заказов в работе", color="#C2B2A9", italic=True, size=14),
                        alignment=ft.Alignment(0, 0),
                        padding=20
                    )
                )
                
            if ready_orders:
                for o in ready_orders:
                    col_ready_items.controls.append(OrderCard(o, handle_status_change, handle_cancel))
            else:
                col_ready_items.controls.append(
                    ft.Container(
                        content=ft.Text("Нет готовых к выдаче", color="#C2B2A9", italic=True, size=14),
                        alignment=ft.Alignment(0, 0),
                        padding=20
                    )
                )
                
            column_new.update_count(len(new_orders))
            column_prep.update_count(len(prep_orders))
            column_ready.update_count(len(ready_orders))
            
            new_count_txt.value = str(len(new_orders))
            prep_count_txt.value = str(len(prep_orders))
            ready_count_txt.value = str(len(ready_orders))
            
            page.update()
        except Exception as e:
            print(f"Ошибка при обновлении доски: {e}")
        finally:
            updating = False

    async def auto_refresh_loop():
        while True:
            try:
                await refresh_orders()
            except Exception as e:
                print(f"Ошибка в фоновом цикле автообновления: {e}")
            await asyncio.sleep(3)
            
    asyncio.create_task(auto_refresh_loop())

if __name__ == "__main__":
    
    flet_port = os.getenv("FLET_PORT")
    if flet_port:
        print(f"Запуск Flet в режиме веб-приложения на порту {flet_port}...")
        ft.app(target=main, port=int(flet_port), host="0.0.0.0", view=ft.AppView.WEB_BROWSER)
    else:
        ft.app(target=main)
