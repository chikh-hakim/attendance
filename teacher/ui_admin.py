# teacher/ui_admin.py
from flask import render_template_string

def render_admin_page(content, title="لوحة تحكم المسؤول", active_page=""):
    return render_template_string(f'''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <link rel="icon" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMxYTczZTgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMjAgMTNjMCA1LTMuNSA3LjUtNy42NiA4Ljk1YTEgMSAwIDAgMS0uNjctLjAxQzcuNSAyMC41IDQgMTggNCAxM1Y2YTEgMSAwIDAgMSAxLTFjMiAwIDQuNS0xLjIgNi4yNC0yLjcyYTEuMTcgMS4xNyAwIDAgMSAxLjUyIDBDMTQuNTEgMy44MSAxNyA1IDE5IDVhMSAxIDAgMCAxIDEgMXoiLz48cGF0aCBkPSJNNi4zNzYgMTguOTFhNiA2IDAgMCAxIDExLjI0OS4wMDMiLz48Y2lyY2xlIGN4PSIxMiIgY3k9IjExIiByPSI0Ii8+PC9zdmc+" type="image/svg+xml">
        <title>{title} - Algorix.CH</title>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f7fa;
                color: #24292e;
                display: flex;
                min-height: 100vh;
            }}
            /* ============= SIDEBAR ============= */
            .sidebar {{
                width: 260px;
                background: #1a73e8;
                color: white;
                height: 100vh;
                position: fixed;
                top: 0;
                right: 0;
                box-shadow: -2px 0 10px rgba(0,0,0,0.1);
                z-index: 100;
                transition: transform 0.3s ease;
            }}
            .sidebar-header {{
                padding: 24px 20px;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }}
            .logo {{
                font-size: 22px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
            .logo span {{
                color: #fbbc04;
            }}
            .nav-links {{
                padding: 20px 0;
            }}
            .nav-item {{
                padding: 0 20px;
                margin-bottom: 4px;
            }}
            .nav-link {{
                display: flex;
                align-items: center;
                padding: 12px 16px;
                color: rgba(255,255,255,0.9);
                text-decoration: none;
                border-radius: 8px;
                transition: all 0.2s;
            }}
            .nav-link:hover {{
                background: rgba(255,255,255,0.1);
                color: white;
            }}
            .nav-link.active {{
                background: rgba(255,255,255,0.2);
                color: white;
            }}
            .nav-link i {{
                margin-left: 16px;
                font-size: 18px;
            }}
            /* ============= MAIN CONTENT ============= */
            .main {{
                flex: 1;
                margin-right: 260px;
                padding: 24px;
            }}
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 24px;
                padding-bottom: 16px;
                border-bottom: 1px solid #e0e0e0;
            }}
            .page-title {{
                font-size: 24px;
                font-weight: 700;
                color: #1a73e8;
            }}
            .logout-btn {{
                background: #d93025;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s;
            }}
            .logout-btn:hover {{
                background: #b3261e;
            }}
            /* ============= MOBILE SIDEBAR ============= */
            @media (max-width: 768px) {{
                .sidebar {{
                    transform: translateX(260px);
                }}
                .sidebar.open {{
                    transform: translateX(0);
                }}
                .main {{
                    margin-right: 0;
                }}
                .mobile-menu-btn {{
                    display: block;
                    background: #1a73e8;
                    color: white;
                    border: none;
                    width: 40px;
                    height: 40px;
                    border-radius: 8px;
                    font-size: 18px;
                    cursor: pointer;
                }}
            }}
            .mobile-menu-btn {{
                display: none;
            }}
            /* ============= FOOTER ============= */
            footer {{
                margin-top: 40px;
                padding: 16px;
                background: #f8f9fa;
                text-align: center;
                border-radius: 8px;
                font-size: 13px;
                color: #5f6368;
                border: 1px solid #e0e0e0;
            }}
        </style>
    </head>
    <body>
        <!-- Mobile Menu Button -->
        <div class="mobile-menu-btn" onclick="toggleSidebar()">☰</div>
        
        <!-- Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-header">
                <div class="logo">Algorix<span>.</span>CH</div>
            </div>
            <nav class="nav-links">
                <div class="nav-item">
                    <a href="/admin/teachers" class="nav-link {'active' if active_page == 'teachers' else ''}">
                        <span>إدارة المدرسين</span>
                        <i>👨‍🏫</i>
                    </a>
                </div>
                <div class="nav-item">
                    <a href="/admin/messages" class="nav-link {'active' if active_page == 'messages' else ''}">
                        <span>رسائل الاتصال</span>
                        <i>📨</i>
                    </a>
                </div>
                <div class="nav-item">
                    <a href="/admin/settings" class="nav-link" style="opacity: 0.6; pointer-events: none;">
                        <span>الإعدادات</span>
                        <i>⚙️</i>
                    </a>
                </div>
            </nav>
        </aside>

        <!-- Main Content -->
        <main class="main">
            <div class="header">
                <h1 class="page-title">{title}</h1>
                <button class="logout-btn" onclick="location.href='/admin/logout'">تسجيل الخروج</button>
            </div>
            
            {content}
            
            <footer>
                Designed by Chikh Abdelhakim — Algorix.CH © 2025. All Rights Reserved.
            </footer>
        </main>

        <script>
            function toggleSidebar() {{
                const sidebar = document.getElementById('sidebar');
                sidebar.classList.toggle('open');
            }}
            
            // Close sidebar when clicking outside on mobile
            document.addEventListener('click', function(event) {{
                const sidebar = document.getElementById('sidebar');
                const menuBtn = document.querySelector('.mobile-menu-btn');
                if (window.innerWidth <= 768) {{
                    if (!sidebar.contains(event.target) && !menuBtn.contains(event.target)) {{
                        sidebar.classList.remove('open');
                    }}
                }}
            }});
        </script>
    </body>
    </html>
    ''')