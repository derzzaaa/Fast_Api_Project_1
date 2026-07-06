import flet as ft
import datetime

def get_elapsed_time_str(created_at: datetime.datetime) -> str:
    
    now = datetime.datetime.utcnow()
    delta = now - created_at
    minutes = int(delta.total_seconds() / 60)
    
    if minutes < 1:
        return "только что"
    elif minutes < 60:
        return f"{minutes} мин назад"
    else:
        hours = minutes // 60
        return f"{hours} ч {minutes % 60} мин назад"

class OrderItemRow(ft.Container):
    
    def __init__(self, name: str, amount: int, price: float):
        super().__init__()
        self.bgcolor = "#3E3530"
        self.border_radius = 8
        self.padding = ft.Padding.symmetric(horizontal=12, vertical=8)
        self.margin = ft.Margin.only(bottom=4)
        
        qty_badge = ft.Container(
            content=ft.Text(
                value=str(amount),
                color="#FFFFFF",
                weight=ft.FontWeight.BOLD,
                size=14,
            ),
            alignment=ft.Alignment(0, 0),
            bgcolor="#D4A373",
            width=28,
            height=28,
            border_radius=14,
        )
        
        item_name = ft.Text(
            value=name,
            color="#F5EBE6",
            size=14,
            weight=ft.FontWeight.W_500,
            overflow=ft.TextOverflow.ELLIPSIS,
            expand=True,
        )
        
        item_price = ft.Text(
            value=f"{int(price * amount)} Р",
            color="#C2B2A9",
            size=13,
            weight=ft.FontWeight.W_400,
        )
        
        self.content = ft.Row(
            controls=[
                qty_badge,
                ft.VerticalDivider(width=8, color=ft.Colors.TRANSPARENT),
                item_name,
                item_price
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

class OrderCard(ft.Container):
    
    def __init__(self, order, on_status_change, on_cancel):
        super().__init__()
        self.order = order
        self.on_status_change = on_status_change
        self.on_cancel = on_cancel
        
        self.bgcolor = "#2B2421"
        self.border_radius = 12
        self.padding = ft.Padding.all(14)
        self.border = ft.Border.all(1, "#4A3E39")
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.3, "#000000"),
            offset=ft.Offset(0, 4)
        )
        self.margin = ft.Margin.only(bottom=10)
        
        self.build_card()
        
    async def start_cooking(self, e):
        await self.on_status_change(self.order.id, "готовится", self.order.order_number)

    async def mark_ready(self, e):
        await self.on_status_change(self.order.id, "готов", self.order.order_number)

    async def deliver_order(self, e):
        await self.on_status_change(self.order.id, "выдан", self.order.order_number)

    async def cancel_order(self, e):
        await self.on_cancel(self.order.id, self.order.order_number)

    def build_card(self):
        elapsed_str = get_elapsed_time_str(self.order.created_at)
        
        status_color = "#FF9F1C"
        status_text = "Новый"
        if self.order.status == "готовится":
            status_color = "#0496FF"
            status_text = "Готовится"
        elif self.order.status == "готов":
            status_color = "#2EC4B6"
            status_text = "Готов"
            
        header = ft.Row(
            controls=[
                ft.Text(
                    value=f"Заказ #{self.order.order_number}",
                    color="#F5EBE6",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(
                    content=ft.Text(
                        value=status_text.upper(),
                        color="#FFFFFF",
                        size=10,
                        weight=ft.FontWeight.BOLD,
                    ),
                    bgcolor=status_color,
                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                    border_radius=20,
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        user_info = ft.Row(
            controls=[
                ft.Icon(ft.Icons.PERSON_OUTLINE, color="#C2B2A9", size=16),
                ft.Text(
                    value=self.order.user.username if self.order.user else "Гость",
                    color="#C2B2A9",
                    size=13,
                    weight=ft.FontWeight.W_500,
                ),
                ft.VerticalDivider(width=10, color=ft.Colors.TRANSPARENT),
                ft.Icon(ft.Icons.ACCESS_TIME_ROUNDED, color="#C2B2A9", size=16),
                ft.Text(
                    value=elapsed_str,
                    color="#C2B2A9",
                    size=13,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        items_column = ft.Column(
            controls=[
                OrderItemRow(item.name, item.amount, item.price)
                for item in self.order.items
            ],
            spacing=2,
        )
        
        action_row = ft.Row(alignment=ft.MainAxisAlignment.END, spacing=8)
        
        cancel_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
            icon_color="#E76F51",
            tooltip="Отменить заказ",
            on_click=self.cancel_order,
            icon_size=20,
        )
        
        if self.order.status == "новый":
            btn = ft.ElevatedButton(
                content="Начать готовить",
                icon=ft.Icons.PLAY_ARROW_ROUNDED,
                bgcolor="#0496FF",
                color="#FFFFFF",
                on_click=self.start_cooking,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.all(10),
                )
            )
            action_row.controls.extend([cancel_btn, btn])
            
        elif self.order.status == "готовится":
            btn = ft.ElevatedButton(
                content="Готов",
                icon=ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
                bgcolor="#2EC4B6",
                color="#FFFFFF",
                on_click=self.mark_ready,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.all(10),
                )
            )
            action_row.controls.extend([cancel_btn, btn])
            
        elif self.order.status == "готов":
            btn = ft.ElevatedButton(
                content="Выдать",
                icon=ft.Icons.DONE_ALL_ROUNDED,
                bgcolor="#D4A373",
                color="#FFFFFF",
                on_click=self.deliver_order,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.all(10),
                )
            )
            action_row.controls.append(btn)
            
        self.content = ft.Column(
            controls=[
                header,
                user_info,
                ft.Divider(height=10, color="#4A3E39"),
                items_column,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                action_row
            ],
            spacing=8,
        )

class KanbanColumn(ft.Container):
    
    def __init__(self, title: str, header_color: str, scroll_container: ft.Column):
        super().__init__()
        self.expand = True
        self.bgcolor = "#1A1715"
        self.border_radius = 12
        self.padding = ft.Padding.all(12)
        self.border = ft.Border.all(1, "#362E2A")
        
        self.title_text = ft.Text(
            value=title,
            color="#F5EBE6",
            size=16,
            weight=ft.FontWeight.BOLD,
        )
        
        self.count_badge = ft.Container(
            content=ft.Text(
                value="0",
                color="#1A1715",
                weight=ft.FontWeight.BOLD,
                size=12,
            ),
            bgcolor=header_color,
            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
            border_radius=10,
        )
        
        column_header = ft.Row(
            controls=[
                self.title_text,
                self.count_badge
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        self.content = ft.Column(
            controls=[
                column_header,
                ft.Divider(height=15, color=header_color, thickness=2),
                ft.Container(
                    content=scroll_container,
                    expand=True,
                )
            ],
            spacing=5,
        )
        
    def update_count(self, count: int):
        self.count_badge.content.value = str(count)
        self.count_badge.update()
