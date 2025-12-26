# teacher/ui.py
from flask import render_template_string

def render_page(content, title="الرئيسية", teacher_name="", current_page=""):
    return render_template_string(f'''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMxYTczZTgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTMgNWg4Ii8+PHBhdGggZD0iTTEzIDEyaDgiLz48cGF0aCBkPSJNMTMgMTloOCIvPjxwYXRoIGQ9Im0zIDE3IDIgMiA0LTQiLz48cGF0aCBkPSJtMyA3IDIgMiA0LTQiLz48L3N2Zz4=" type="image/svg+xml">
        <title>{title}</title>
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
                background-color: #fafbfc;
                color: #24292e;
                line-height: 1.5;
            }}
            .container {{
                max-width: 960px;
                margin: 0 auto;
                padding: 0 20px;
            }}

            /* ============= NAVBAR ============= */
            nav {{
                background: white;
                box-shadow: 0 1px 4px rgba(0,0,0,0.08);
                position: sticky;
                top: 0;
                z-index: 100;
            }}
            .navbar {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                height: 50px;
              
                margin: 0 auto;
                padding: 0 20px;
            }}
            .logo {{
                font-weight: 700;
                font-size: 18px;
                color: #1a73e8;
                text-decoration: none;
                letter-spacing: -0.3px;
            }}
            .nav-links {{
                display: flex;
                list-style: none;
                margin: 0;
                padding: 0;
                gap: 20px;
            }}
            .nav-links a {{
                text-decoration: none;
                color: #5f6368;
                font-weight: 500;
                font-size: 14px;
                padding: 8px 12px;
                border-radius: 6px;
                transition: all 0.2s ease;
                letter-spacing: -0.1px;
            }}
            .nav-links a:hover {{
                background-color: #f1f3f4;
                color: #1a73e8;
            }}
            .nav-links a.active {{
                background-color: #e8f0fe;
                color: #1a73e8;
            }}
            .greeting {{
                font-size: 14px;
                color: #5f6368;
                font-weight: 500;
                letter-spacing: -0.1px;
            }}
            .logout {{
                color: #d93025 !important;
            }}
            .logout:hover {{
                background-color: #fce8e6 !important;
                color: #d93025 !important;
            }}

            /* ============= MOBILE MENU ============= */
            .hamburger {{
                display: none;
                flex-direction: column;
                cursor: pointer;
                padding: 6px;
                border-radius: 50%;
                transition: background 0.2s;
            }}
            .hamburger:hover {{
                background: #f1f3f4;
            }}
            .hamburger span {{
                width: 20px;
                height: 2px;
                background: #5f6368;
                margin: 3px 0;
                transition: 0.3s;
                border-radius: 2px;
            }}
            .hamburger.active span:nth-child(1) {{
                transform: translateY(5px) rotate(45deg);
            }}
            .hamburger.active span:nth-child(2) {{
                opacity: 0;
            }}
            .hamburger.active span:nth-child(3) {{
                transform: translateY(-5px) rotate(-45deg);
            }}

            /* ============= MAIN & FOOTER ============= */
            main {{
                padding: 32px 0 48px;
            }}
            footer {{
                padding: 20px;
                background: #f8f9fa;
                text-align: center;
                border-top: 1px solid #eaeaec;
                font-size: 13px;
                color: #70757a;
                font-weight: 500;
                letter-spacing: -0.1px;
                border-radius: 8px;
            }}

            /* ============= MOBILE STYLES ============= */
            @media (max-width: 1064px) {{
                .hamburger {{
                    display: flex;
                }}
                .nav-links {{
                    position: absolute;
                    top: 56px;
                    right: 20px;
                    background: white;
                    flex-direction: column;
                    width: calc(100% - 40px);
                    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
                    border-radius: 12px;
                    padding: 12px 0;
                    gap: 4px;
                    display: none;
                    z-index: 10;
                }}
                .nav-links.active {{
                    display: flex;
                }}
                .nav-links a {{
                    
                    padding: 6px 11px;
                    font-size: 15px;
                    text-align: right;
                    border-radius: 8px;
                }}
         
                .greeting {{
                    display: none;
                }}
                main {{
                    padding: 24px 0 40px;
                }}
            }}
        </style>
    </head>
    <body>
        <nav>
            <div class="navbar">
            
                    <div class="greeting"><a href="/dashboard" class="logo"> مرحبًا، {teacher_name}</a> </div>
                <div class="hamburger" id="hamburger" onclick="toggleMenu()">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>

                <ul class="nav-links" id="navLinks">
                 <li><a href="/dashboard" class="{'active' if current_page == 'dashboard' else ''}">الرئيسية</a></li>
                <li><a href="/attendance" class="{'active' if current_page == 'attendance' else ''}">تسجيل الحضور</a></li>
                <li><a href="/statistics" class="{'active' if current_page == 'statistics' else ''}">إحصائيات</a></li>
                    <li><a href="/upload" class="{'active' if current_page == 'upload' else ''}">اضافة تلاميذ</a></li>
                    <li><a href="/groups" class="{'active' if current_page == 'groups' else ''}">تقسيم أفواج</a></li>
                    <li><a href="/contact" class="{'active' if current_page == 'contact' else ''}">اتصل بالمسؤول</a></li>
                    <li><a href="/logout" class="logout">تسجيل الخروج</a></li>
                </ul>
               <a href="/dashboard" class="logo">Algorix<span style=" color: #fbbc04;">.</span>CH</a>
            
            </div>
        </nav>

        <div class="container">
            <main>{content}</main>
            <footer>
                Designed by Chikh Abdelhakim — Algorix.CH © 2025. All Rights Reserved.
            </footer>
        </div>

        <script>
            function toggleMenu() {{
                const nav = document.getElementById('navLinks');
                const burger = document.getElementById('hamburger');
                nav.classList.toggle('active');
                burger.classList.toggle('active');
            }}

            // Close menu when clicking outside
            document.addEventListener('click', function(event) {{
                const nav = document.getElementById('navLinks');
                const burger = document.getElementById('hamburger');
                if (!nav.contains(event.target) && !burger.contains(event.target)) {{
                    nav.classList.remove('active');
                    burger.classList.remove('active');
                }}
            }});
        </script>
    </body>
    </html>
    ''')