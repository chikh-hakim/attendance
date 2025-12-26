# teacher/routes/auth.py
from flask import Blueprint, request, redirect, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Teacher

auth_bp = Blueprint('auth', __name__)

def render_page(content, title="نظام الأستاذ"):
    return render_template_string('''
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="utf-8">
       <link rel="icon" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiMxYTczZTgiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTMgNWg4Ii8+PHBhdGggZD0iTTEzIDEyaDgiLz48cGF0aCBkPSJNMTMgMTloOCIvPjxwYXRoIGQ9Im0zIDE3IDIgMiA0LTQiLz48cGF0aCBkPSJtMyA3IDIgMiA0LTQiLz48L3N2Zz4=" type="image/svg+xml">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>''' + title + '''</title>
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                padding: 15px;
                background: #f9fbfd;
                color: #333;
                max-width: 750px;
                margin: 0 auto;
            }
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 0;
                border-bottom: 2px solid #0056b3;
                margin-bottom: 25px;
            }
            header .logo {
                font-weight: bold;
                font-size: 1.4em;
                color: #0056b3;
                letter-spacing: -0.5px;
            }
            h2 {
                color: #0056b3;
                margin: 25px 0 20px;
                text-align: center;
            }
            label {
                display: block;
                margin: 12px 0 6px;
                font-weight: 600;
                color: #444;
            }
            input, button {
                width: 100%;
                padding: 12px;
                font-size: 16px;
                border: 1px solid #ccc;
                border-radius: 8px;
                margin: 6px 0;
            }
            input:focus {
                outline: none;
                border-color: #0056b3;
                box-shadow: 0 0 0 2px rgba(0, 86, 179, 0.2);
            }
            .password-wrapper {
                position: relative;
            }
            .password-wrapper input {
                padding-left: 48px; /* space for LEFT icon */
            }
            .password-toggle {
                position: absolute;
                left: 12px;
                top: 50%;
                transform: translateY(-50%);
                cursor: pointer;
                user-select: none;
            }
            .eye-icon {
                width: 20px;
                height: 20px;
                vertical-align: middle;
                color: #0056b3;
            }
            button {
                background: #0056b3;
                color: white;
                border: none;
                font-weight: bold;
                cursor: pointer;
                margin-top: 15px;
            }
            button:hover {
                background: #00408f;
            }
            p {
                text-align: center;
                margin: 20px 0 0;
                color: #555;
            }
            a {
                color: #0056b3;
                text-decoration: none;
                font-weight: 600;
            }
            a:hover {
                text-decoration: underline;
            }
            footer {
                margin-top: 40px;
                padding: 12px;
                background: #f0f4f8;
                text-align: center;
                border-top: 1px solid #dfe6ee;
                font-size: 13px;
                color: #666;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <header>
            <div class="logo">Algorix.CH</div>
            <div></div>
        </header>
        <main>''' + content + '''</main>
        <footer>
            Designed by Chikh Abdelhakim — Algorix.CH © 2025. All Rights Reserved.
        </footer>
    </body>
    </html>
    ''')


def get_register_form():
    return '''
    <form method="post">
        <label>اسم المستخدم</label>
        <input name="username" required>

        <label>البريد الإلكتروني</label>
        <input name="email" type="email" required>

        <label>كلمة المرور</label>
        <div class="password-wrapper">
            <span class="password-toggle" onclick="togglePassword()">
                <!-- Open Eye -->
                <svg id="eye-open" class="eye-icon" style="display:none;" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/>
                    <circle cx="12" cy="12" r="3"/>
                </svg>
                <!-- Closed Eye -->
                <svg id="eye-closed" class="eye-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/>
                    <path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/>
                    <path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/>
                    <path d="m2 2 20 20"/>
                </svg>
            </span>
            <input type="password" name="password" id="password" required>
        </div>

        <label>المادة التي تُدرّسها</label>
        <input name="subject" required placeholder="مثال: الرياضيات، الفيزياء...">

        <button type="submit">إنشاء الحساب</button>
    </form>
    <p>لديك حساب؟ <a href="/login">سجّل دخولك</a></p>

    <script>
        function togglePassword() {
            const input = document.getElementById('password');
            const eyeOpen = document.getElementById('eye-open');
            const eyeClosed = document.getElementById('eye-closed');

            if (input.type === 'password') {
                input.type = 'text';
                eyeOpen.style.display = 'block';
                eyeClosed.style.display = 'none';
            } else {
                input.type = 'password';
                eyeOpen.style.display = 'none';
                eyeClosed.style.display = 'block';
            }
        }
    </script>
    '''


def get_login_form():
    return '''
    <form method="post">
        <label>اسم المستخدم أو البريد الإلكتروني</label>
        <input name="username" required>

        <label>كلمة المرور</label>
        <div class="password-wrapper">
            <span class="password-toggle" onclick="togglePassword()">
                <!-- Open Eye -->
                <svg id="eye-open" class="eye-icon" style="display:none;" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"/>
                    <circle cx="12" cy="12" r="3"/>
                </svg>
                <!-- Closed Eye -->
                <svg id="eye-closed" class="eye-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"/>
                    <path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"/>
                    <path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"/>
                    <path d="m2 2 20 20"/>
                </svg>
            </span>
            <input type="password" name="password" id="password" required>
        </div>

        <button type="submit">تسجيل الدخول</button>
    </form>
    <p>ليس لديك حساب؟ <a href="/register">أنشئ واحدًا الآن</a></p>

    <script>
        function togglePassword() {
            const input = document.getElementById('password');
            const eyeOpen = document.getElementById('eye-open');
            const eyeClosed = document.getElementById('eye-closed');

            if (input.type === 'password') {
                input.type = 'text';
                eyeOpen.style.display = 'block';
                eyeClosed.style.display = 'none';
            } else {
                input.type = 'password';
                eyeOpen.style.display = 'none';
                eyeClosed.style.display = 'block';
            }
        }
    </script>
    '''

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        subject = request.form['subject'].strip()

        if not all([username, email, password, subject]):
            msg = '<p style="color:#d00; text-align:center;">جميع الحقول مطلوبة!</p>'
            return render_page(msg + get_register_form(), "إنشاء حساب")

        if Teacher.query.filter_by(username=username).first():
            msg = '<p style="color:#d00; text-align:center;">اسم المستخدم مستخدم بالفعل!</p>'
            return render_page(msg + get_register_form(), "إنشاء حساب")

        if Teacher.query.filter_by(email=email).first():
            msg = '<p style="color:#d00; text-align:center;">البريد الإلكتروني مستخدم بالفعل!</p>'
            return render_page(msg + get_register_form(), "إنشاء حساب")

        try:
            teacher = Teacher(
                username=username,
                email=email,
                password=generate_password_hash(password),
                subject=subject
            )
            db.session.add(teacher)
            db.session.commit()
            return redirect('/login')
        except Exception as e:
            db.session.rollback()
            print(f"Account creation error: {e}")
            msg = '<p style="color:#d00; text-align:center;">حدث خطأ أثناء إنشاء الحساب. يرجى المحاولة مرة أخرى.</p>'
            return render_page(msg + get_register_form(), "إنشاء حساب")

    # ✅ Only reached on GET request
    return render_page(get_register_form(), "إنشاء حساب")


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form['username'].strip()
        password = request.form['password']

        teacher = Teacher.query.filter(
            (Teacher.username == user_input) | (Teacher.email == user_input)
        ).first()

        if teacher and check_password_hash(teacher.password, password):
            session['teacher_id'] = teacher.id
            session.permanent = True
            return redirect('/dashboard')
        else:
            msg = '<p style="color:#d00; text-align:center;">بيانات الدخول غير صحيحة!</p>'
            return render_page(msg + get_login_form(), "تسجيل الدخول")

    return render_page(get_login_form(), "تسجيل الدخول")


@auth_bp.route('/logout')
def logout():
    session.pop('teacher_id', None)
    return redirect('/login')