import flet as ft
import json
from datetime import datetime
import google.generativeai as genai

def main(page: ft.Page):
    page.title = "SofiaGPT"
    page.bgcolor = "#fca2cf"
    page.window_width = 400 
    page.window_height = 900
    page.scroll = False
    page.padding = 0
    page.rtl = False
    
    messages = []
    history = {}
    current_chat_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    HISTORY_FILE = "chat_history.json"
    
    # Hardcoded API key and model
    gemini_api_key = "AIzaSyBrSpD_nQe8zU1JHStOYjNPnVr5B48EktY"  # Replace with your actual API key
    gemini_model = "gemini-1.5-flash"
    
    def load_history():
        try:
            with open(HISTORY_FILE, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
    
    def save_history(history):
        with open(HISTORY_FILE, "w") as file:
            json.dump(history, file, indent=4)
    
    history = load_history()
    
    chat_column = ft.Column(
        spacing=16,
        scroll=None, 
        expand=True,  
    )
    
    chat_list_view = ft.ListView(
        controls=[chat_column],
        expand=True,
        spacing=0,
        padding=0,
        auto_scroll=True,  
    )
    
    chat_area = ft.Container(
        content=chat_list_view,
        expand=True,
        padding=ft.padding.only(left=12, right=12, top=8, bottom=16),
    )
    
    user_message = ft.TextField(
        hint_text="Type your message...", 
        expand=True,
        bgcolor="pink", 
        border_radius=20,
        text_size=14,
        on_submit=lambda e: send_message(e),
        border=ft.border.all(0),
        content_padding=ft.padding.only(left=16, right=16, top=12, bottom=12)
    )
    
    send_button = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED, 
        tooltip="Send", 
        icon_color="red",
        icon_size=24
    )
    
    input_row = ft.Container(
        content=ft.Row(
            [user_message, send_button],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=ft.padding.only(left=12, right=12, top=8, bottom=8),
        bgcolor="#f55ea9",
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.colors.with_opacity(0.2, "black"),
            offset=ft.Offset(0, -5)
        ),
        height=60
    )
    
    def format_timestamp():
        now = datetime.now()
        return now.strftime("%I:%M %p")
    
    def copy_to_clipboard(e, text):
        page.set_clipboard(text)
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Message copied to clipboard"),
            action="OK",
            duration=2000
        )
        page.snack_bar.open = True
        page.update()
    
    def display_messages():
        chat_column.controls.clear()
        for msg in messages:
            is_user = msg["role"] == "user"
            label = "Me" if is_user else "sofia"
            
            message_text = msg["content"]
            
            if is_user:
                message_content = ft.Column([
                    ft.Text(
                        label,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#757575"
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                message_text,
                                size=14,
                                color="#000000",
                                width=page.window_width * 0.65,
                                max_lines=None,
                                overflow="visible",
                                text_align=ft.TextAlign.RIGHT,
                                selectable=True
                            ),
                            ft.Container(
                                content=ft.Text(
                                    format_timestamp(),
                                    size=10,
                                    color=ft.colors.with_opacity(0.5, "black")
                                ),
                                alignment=ft.alignment.bottom_right,
                                padding=ft.padding.only(top=4)
                            )
                        ]),
                        padding=12,
                        bgcolor="#DCF8C6",
                        border_radius=12,
                        width=page.window_width * 0.7
                    )
                ])
            else:
                message_content = ft.Column([
                    ft.Text(
                        label,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#757575"
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(
                                message_text,
                                size=14,
                                color="#000000",
                                width=page.window_width * 0.65,
                                max_lines=None,
                                overflow="visible",
                                text_align=ft.TextAlign.RIGHT,
                                selectable=True
                            ),
                            ft.Row([
                                ft.Text(
                                    format_timestamp(),
                                    size=10,
                                    color=ft.colors.with_opacity(0.5, "black")
                                ),
                                ft.IconButton(
                                    icon=ft.icons.COPY,
                                    icon_size=16,
                                    tooltip="Copy",
                                    on_click=lambda e, m=message_text: copy_to_clipboard(e, m)
                                )
                            ], 
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=0
                            )
                        ]),
                        padding=12,
                        bgcolor="white",
                        border_radius=12,
                        width=page.window_width * 0.7
                    )
                ])
            
            chat_column.controls.append(
                ft.Row(
                    [message_content],
                    alignment=ft.MainAxisAlignment.END if is_user else ft.MainAxisAlignment.START
                )
            )
        page.update()
     
        if len(chat_column.controls) > 0:
            chat_list_view.scroll_to(offset=float('inf'), duration=300)
            page.update()
    
    def send_message(e):
        user_input = user_message.value.strip()
        if not user_input:
            return
        
        if not gemini_api_key:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Please set your Gemini API key"),
                action="OK",
                duration=3000
            )
            page.snack_bar.open = True
            page.update()
            return
        
        user_msg_content = ft.Column([
            ft.Text(
                "you",
                size=12,
                weight=ft.FontWeight.BOLD,
                color="#f55ea9"
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        user_input,
                        size=14,
                        color="#000000",
                        width=page.window_width * 0.65,
                        max_lines=None,
                        overflow="visible",
                        text_align=ft.TextAlign.RIGHT,
                        selectable=True
                    ),
                    ft.Container(
                        content=ft.Text(
                            format_timestamp(),
                            size=10,
                            color=ft.colors.with_opacity(0.5, "black")
                        ),
                        alignment=ft.alignment.bottom_right,
                        padding=ft.padding.only(top=4)
                    )
                ]),
                padding=12,
                bgcolor="#DCF8C6",
                border_radius=12,
                width=page.window_width * 0.7
            )
        ])
        
        chat_column.controls.append(
            ft.Row(
                [user_msg_content],
                alignment=ft.MainAxisAlignment.END
            )
        )
    
        chat_list_view.scroll_to(offset=float('inf'), duration=300)
        page.update()
        
        messages.append({"role": "user", "content": user_input})
        
        typing_indicator = ft.Row([
            ft.ProgressRing(width=16, height=16),
            ft.Text("  Thinking...", size=12, color="#757575")
        ])
        typing_row = ft.Row([typing_indicator], alignment=ft.MainAxisAlignment.START)
        chat_column.controls.append(typing_row)
    
        chat_list_view.scroll_to(offset=float('inf'), duration=300)
        page.update()
        
        try:
            genai.configure(api_key=gemini_api_key)
            
            chat_history = []
            for msg in messages:
                if msg["role"] == "user":
                    chat_history.append({"role": "user", "parts": [msg["content"]]})
                else:
                    chat_history.append({"role": "model", "parts": [msg["content"]]})
            
            model = genai.GenerativeModel(gemini_model)
            response = model.generate_content(chat_history)
            bot_reply = response.text
            
            messages.append({"role": "assistant", "content": bot_reply})
        except Exception as err:
            bot_reply = f"Error: {err}"
            messages.append({"role": "assistant", "content": bot_reply})
        
        chat_column.controls.remove(typing_row)
        
        bot_msg_content = ft.Column([
            ft.Text(
                "Sofiaaaaaa",
                size=12,
                weight=ft.FontWeight.BOLD,
                color="#f55ea9"
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        bot_reply,
                        size=14,
                        color="#000000",
                        width=page.window_width * 0.65,
                        max_lines=None,
                        overflow="visible",
                        text_align=ft.TextAlign.RIGHT,
                        selectable=True
                    ),
                    ft.Row([
                        ft.Text(
                            format_timestamp(),
                            size=10,
                            color=ft.colors.with_opacity(0.5, "black")
                        ),
                        ft.IconButton(
                            icon=ft.icons.COPY,
                            icon_size=16,
                            tooltip="Copy",
                            on_click=lambda e, m=bot_reply: copy_to_clipboard(e, m)
                        )
                    ], 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=0
                    )
                ]),
                padding=12,
                bgcolor="white",
                border_radius=12,
                width=page.window_width * 0.7
            )
        ])
        
        chat_column.controls.append(
            ft.Row(
                [bot_msg_content],
                alignment=ft.MainAxisAlignment.START
            )
        )
        
        history[current_chat_id] = messages
        save_history(history)
        
        user_message.value = ""
     
        chat_list_view.scroll_to(offset=float('inf'), duration=300)
        page.update()
    
    send_button.on_click = send_message
    
    def new_chat(e):
        nonlocal messages, current_chat_id
        messages = []
        current_chat_id = datetime.now().strftime("%Y%m%d%H%M%S")
        display_messages()
    
    def show_history(e):
        page.controls.clear()
        
        def open_chat(e):
            nonlocal current_chat_id, messages
            current_chat_id = e.control.data
            messages = history[current_chat_id]
            load_main_interface()
            
        history_items = []
        
        back_button = ft.IconButton(
            icon=ft.icons.ARROW_BACK,
            tooltip="Back",
            on_click=lambda e: load_main_interface()
        )
        
        app_bar = ft.Container(
            content=ft.Row(
                [
                    back_button,
                    ft.Text("Chat History", size=20, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=16,
            bgcolor="#ffffff",
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.with_opacity(0.1, "black")
            )
        )
        
        for chat_id in history.keys():
            preview = ""
            chat_date = ""
            if history[chat_id]:
                for msg in history[chat_id]:
                    if msg["role"] == "user":
                        preview = msg["content"]
                        break
                
                try:
                    chat_datetime = datetime.strptime(chat_id, "%Y%m%d%H%M%S")
                    chat_date = chat_datetime.strftime("%b %d, %Y %I:%M %p")
                except:
                    chat_date = "Unknown date"
            
            if len(preview) > 40:
                preview = preview[:40] + "..."
                
            history_items.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.ListTile(
                            leading=ft.Icon(ft.icons.CHAT),
                            title=ft.Text(chat_date),
                            subtitle=ft.Text(preview if preview else "Empty chat"),
                            on_click=open_chat,
                            data=chat_id
                        ),
                        padding=ft.padding.symmetric(vertical=5)
                    ),
                    margin=5,
                    elevation=1
                )
            )
        
        history_list = ft.ListView(
            controls=history_items,
            expand=True,
            spacing=0,
            padding=10,
            auto_scroll=False
        )
        
        if len(history_items) == 0:
            history_list.controls.append(
                ft.Container(
                    content=ft.Text("No chat history found", size=16, color="#757575"),
                    alignment=ft.alignment.center,
                    margin=20
                )
            )
        
        page.add(
            ft.Column([
                app_bar,
                ft.Container(
                    content=history_list,
                    expand=True
                )
            ], spacing=0, expand=True)
        )
        page.update()
    
    def load_main_interface():
        page.controls.clear()
        
        app_title = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.icons.HISTORY,
                        tooltip="Chat History",
                        on_click=show_history
                    ),
                    ft.Container(
                        content=ft.Text("SofiaGPT", size=20, weight=ft.FontWeight.BOLD),
                        expand=True,
                        alignment=ft.alignment.center
                    ),
                    ft.IconButton(
                        icon=ft.icons.ADD_CIRCLE_OUTLINE,
                        tooltip="New Chat",
                        on_click=new_chat
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=16,
            bgcolor="#ffffff",
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=5,
                color=ft.colors.with_opacity(0.1, "black")
            )
        )
        
        main_column = ft.Column([
            app_title,
            chat_area,
            input_row
        ], spacing=0, expand=True)
        
        page.add(main_column)
        display_messages()
        
        if len(messages) > 0:
            chat_list_view.scroll_to(offset=float('inf'), duration=300)
            page.update()
        
        page.update()
    
    load_main_interface()
    
    page.on_keyboard_event = lambda e: print(f"Key event: {e.key}")
    
    if not gemini_api_key:
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Please replace the API key in the code"),
            action="OK",
            duration=5000
        )
        page.snack_bar.open = True
        page.update()

ft.app(target=main)