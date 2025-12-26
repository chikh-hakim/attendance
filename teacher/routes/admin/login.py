# teacher/routes/admin/login.py
from flask import Blueprint, request, redirect, session, render_template_string
import os
from dotenv import load_dotenv

load_dotenv()

admin_login_bp = Blueprint('admin_login', __name__)

def render_login_page(error=None):
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMxYTczZTgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMjAgMTNjMCA1LTMuNSA3LjUtNy42NiA4Ljk1YTEgMSAwIDAgMS0uNjctLjAxQzcuNSAyMC41IDQgMTggNCAxM1Y2YTEgMSAwIDAgMSAxLTFjMiAwIDQuNS0xLjIgNi4yNC0yLjcyYTEuMTcgMS4xNyAwIDAgMSAxLjUyIDBDMTQuNTEgMy44MSAxNyA1IDE5IDVhMSAxIDAgMCAxIDEgMXoiLz48cGF0aCBkPSJNNi4zNzYgMTguOTFhNiA2IDAgMCAxIDExLjI0OS4wMDMiLz48Y2lyY2xlIGN4PSIxMiIgY3k9IjExIiByPSI0Ii8+PC9zdmc+" type="image/svg+xml">
        <title>لوحة تحكم المسؤول</title>
        <style>
            body {
                font-family: Tahoma, sans-serif;
                background: #f5f7fa;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
            }
            .login-box {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                width: 350px;
                text-align: center;
            }
            .logo {
                font-weight: bold;
                color: #1a73e8;
                font-size: 24px;
                margin-bottom: 20px;
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #1a73e8;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                margin-top: 10px;
            }
            .error {
                color: #d32f2f;
                background: #ffebee;
                padding: 10px;
                border-radius: 6px;
                margin: 10px 0;
            }
            .footer {
                margin-top: 20px;
                color: #666;
                font-size: 13px;
            }
        </style>
    </head>
    <body>
        <div class="login-box">
            <div class="logo">Algorix.CH</div>
            <h2>لوحة تحكم المسؤول</h2>
            ''' + (f'<div class="error">{error}</div>' if error else '') + '''
            <form method="POST">
                <input type="text" name="username" placeholder="اسم المستخدم" required>
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <button type="submit">تسجيل الدخول</button>
            </form>
            <div class="footer">
                Designed by Chikh Abdelhakim — Algorix.CH © 2025
            </div>
        </div>
    </body>
    </html>
    ''')

@admin_login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # جلب بيانات المسؤول من .env
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if username == admin_user and password == admin_pass:
            session['admin_logged_in'] = True  # ← جلسة منفصلة!
            return redirect('/admin/teachers')
        else:
            return render_login_page("اسم المستخدم أو كلمة المرور غير صحيحة")
    
    return render_login_page()

@admin_login_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)  # ← إزالة جلسة المسؤول فقط
    return redirect('/admin/login')

# 🔒 حماية جميع صفحات المسؤول
@admin_login_bp.before_app_request
def require_admin_login():
    # تطبيق الحماية فقط على مسارات تبدأ بـ /admin/
    if request.path.startswith('/admin/') and request.endpoint != 'admin_login.login':
        if not session.get('admin_logged_in'):
            return redirect('/admin/login')