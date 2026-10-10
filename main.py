import ssl
import certifi

# Fix SSL certificate verification for macOS
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

import flet as ft
import sqlite3
import urllib.request
import json

def main(page: ft.Page):
    page.title = "AI Knowledge Base Pro (Local Ollama)"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 25
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)

    # UI Elements for Documents
    title_input = ft.TextField(
        label="Document Title", 
        width=450, 
        border_radius=10,
        filled=True
    )
    content_input = ft.TextField(
        label="Document Content", 
        multiline=True, 
        width=450, 
        height=120, 
        border_radius=10,
        filled=True
    )
    search_input = ft.TextField(
        label="Search your knowledge base...", 
        width=450, 
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        filled=True,
        on_change=lambda e: load_documents(search_input.value)
    )
    status_text = ft.Text("", weight=ft.FontWeight.W_500)
    
    docs_list = ft.ListView(expand=1, spacing=12, padding=5, height=300)

    # AI Query UI Elements
    ai_query_input = ft.TextField(
        label="Ask anything about your notes...", 
        width=450,
        prefix_icon=ft.Icons.AUTO_AWESOME,
        border_radius=10,
        filled=True
    )
    ai_response_text = ft.Text(
        "✨ Local AI insights will appear here...", 
        italic=True, 
        color=ft.Colors.BLUE_GREY_400,
        size=15
    )

    def ask_ai(e):
        if not ai_query_input.value:
            ai_response_text.value = "Please enter a question for the AI."
            page.update()
            return

        conn = sqlite3.connect("knowledge_base.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, content FROM documents")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            ai_response_text.value = "No documents found in your knowledge base to query against!"
            page.update()
            return

        # Build context from your local SQLite notes
        context = "\n".join([f"Title: {row[0]}\nContent: {row[1]}\n---" for row in rows])
        prompt = f"You are a helpful AI assistant. Use the following knowledge base context to answer the user's question accurately.\n\nKnowledge Base:\n{context}\n\nQuestion: {ai_query_input.value}"

        ai_response_text.value = "Thinking locally with Ollama..."
        page.update()

        try:
            # Send request to local Ollama API (default port 11434)
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "llama3",  # Change this if you use another model like 'phi3' or 'mistral'
                "prompt": prompt,
                "stream": False
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                ai_response_text.value = res_data.get("response", "No response generated.")
                
        except Exception as ex:
            ai_response_text.value = f"Error connecting to Ollama (Is it running?): {ex}"
        
        page.update()

    ai_btn = ft.Button(
        "Ask Local AI", 
        icon=ft.Icons.AUTO_AWESOME, 
        on_click=ask_ai
    )

    # Edit Dialog Fields
    edit_title_input = ft.TextField(label="Edit Title", width=380, border_radius=8, filled=True)
    edit_content_input = ft.TextField(label="Edit Content", multiline=True, width=380, height=100, border_radius=8, filled=True)
    current_edit_id = ft.Ref[int]()

    def update_document(e):
        if not edit_title_input.value or not edit_content_input.value:
            return
        conn = sqlite3.connect("knowledge_base.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE documents SET title = ?, content = ? WHERE id = ?",
            (edit_title_input.value, edit_content_input.value, current_edit_id.current)
        )
        conn.commit()
        conn.close()
        edit_dialog.open = False
        status_text.value = "✓ Document updated successfully!"
        status_text.color = ft.Colors.GREEN
        load_documents(search_input.value)
        page.update()

    edit_dialog = ft.AlertDialog(
        title=ft.Text("Edit Note", weight=ft.FontWeight.BOLD),
        content=ft.Column([edit_title_input, edit_content_input], tight=True, spacing=15),
        actions=[
            ft.Button("Save Changes", on_click=update_document),
            ft.Button("Cancel", on_click=lambda e: setattr(edit_dialog, 'open', False) or page.update())
        ],
        shape=ft.RoundedRectangleBorder(radius=12)
    )
    page.dialog = edit_dialog

    def open_edit_dialog(doc_id, title, content):
        current_edit_id.current = doc_id
        edit_title_input.value = title
        edit_content_input.value = content
        edit_dialog.open = True
        page.update()

    def delete_document(doc_id):
        conn = sqlite3.connect("knowledge_base.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()
        status_text.value = "🗑 Document deleted."
        status_text.color = ft.Colors.RED
        load_documents(search_input.value)

    def load_documents(query=""):
        docs_list.controls.clear()
        conn = sqlite3.connect("knowledge_base.db")
        cursor = conn.cursor()
        
        if query:
            cursor.execute(
                "SELECT id, title, content FROM documents WHERE title LIKE ? OR content LIKE ?", 
                (f"%{query}%", f"%{query}%")
            )
        else:
            cursor.execute("SELECT id, title, content FROM documents")
            
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            doc_id, title, content = row[0], row[1], row[2]
            docs_list.controls.append(
                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(title, weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(content, color=ft.Colors.OUTLINE)
                            ], expand=True, spacing=4),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_ROUNDED,
                                    icon_color=ft.Colors.INDIGO,
                                    tooltip="Edit Document",
                                    on_click=lambda e, did=doc_id, t=title, c=content: open_edit_dialog(did, t, c)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_ROUNDED,
                                    icon_color=ft.Colors.RED_400,
                                    tooltip="Delete Document",
                                    on_click=lambda e, did=doc_id: delete_document(did)
                                )
                            ], spacing=0)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=15
                    )
                )
            )
        page.update()

    def add_document(e):
        if not title_input.value or not content_input.value:
            status_text.value = "⚠️ Please fill in both fields."
            status_text.color = ft.Colors.RED
            page.update()
            return

        conn = sqlite3.connect("knowledge_base.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO documents (title, content) VALUES (?, ?)", 
                       (title_input.value, content_input.value))
        conn.commit()
        conn.close()

        title_input.value = ""
        content_input.value = ""
        status_text.value = "✓ Document added successfully!"
        status_text.color = ft.Colors.GREEN
        load_documents(search_input.value)

    submit_btn = ft.Button("Save Document", icon=ft.Icons.SAVE_ROUNDED, on_click=add_document)
    load_documents()

    # Styled Tab Contents
    ask_ai_tab = ft.Container(
        content=ft.Column([
            ft.Container(height=5),
            ft.Text("Chat with your Local AI Knowledge Base", size=18, weight=ft.FontWeight.BOLD),
            ai_query_input,
            ai_btn,
            ft.Divider(height=30),
            ft.Text("AI Response", weight=ft.FontWeight.BOLD, size=16),
            ft.Container(
                content=ai_response_text,
                padding=15,
                border_radius=10,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                expand=True
            )
        ], spacing=15),
        padding=15
    )

    manage_docs_tab = ft.Container(
        content=ft.Column([
            ft.Container(height=5),
            ft.Text("Create New Note", size=18, weight=ft.FontWeight.BOLD),
            title_input,
            content_input,
            ft.Row([submit_btn, status_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=30),
            search_input,
            ft.Container(height=5),
            docs_list
        ], scroll=ft.ScrollMode.AUTO, spacing=12),
        padding=15
    )

    page.add(
        ft.Row([
            ft.Icon(ft.Icons.PSYCHOLOGY_ROUNDED, size=32, color=ft.Colors.INDIGO),
            ft.Text("AI Knowledge Base (Local)", size=26, weight=ft.FontWeight.BOLD)
        ], alignment=ft.MainAxisAlignment.START),
        ft.Container(height=5),
        ft.Tabs(
            length=2,
            expand=True,
            content=ft.Column(
                expand=True,
                controls=[
                    ft.TabBar(
                        tabs=[
                            ft.Tab(label="Ask AI", icon=ft.Icons.AUTO_AWESOME),
                            ft.Tab(label="Manage Documents", icon=ft.Icons.FOLDER_SPECIAL_ROUNDED),
                        ]
                    ),
                    ft.TabBarView(
                        expand=True,
                        controls=[
                            ask_ai_tab,
                            manage_docs_tab,
                        ]
                    )
                ]
            )
        )
    )

ft.run(main)