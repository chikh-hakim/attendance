# teacher/app.py
import sys
import os

# === ADD THE 'teacher' FOLDER TO PATH ===
teacher_path = os.path.dirname(os.path.abspath(__file__))
if teacher_path not in sys.path:
    sys.path.insert(0, teacher_path)

# === Keep your original root path ===
root_path = os.path.dirname(teacher_path)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from flask import Flask
from config import Config
from models import db

# مسارات الأستاذ
from teacher.routes.auth import auth_bp
from teacher.routes.dashboard import dashboard_bp
from teacher.routes.statistics import statistics_bp
from teacher.routes.upload import upload_bp
from teacher.routes.groups import groups_bp
from teacher.routes.attendance import attendance_bp
from teacher.routes.contact import contact_bp

# مسارات المسؤول
from teacher.routes.admin.login import admin_login_bp
from teacher.routes.admin.teachers import teachers_bp
from teacher.routes.admin.messages import messages_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # === إعدادات الجلسة الدائمة ===
    app.config['PERMANENT_SESSION_LIFETIME'] = 30 * 24 * 60 * 60  # 30 يومًا
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    db.init_app(app)

    # ✅ Create tables safely
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"⚠️ Database setup error: {e}")

    # تسجيل مسارات الأستاذ
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(contact_bp)

    # تسجيل مسارات المسؤول
    app.register_blueprint(admin_login_bp, url_prefix='/admin')
    app.register_blueprint(teachers_bp, url_prefix='/admin')
    app.register_blueprint(messages_bp, url_prefix='/admin')

    @app.route('/')
    def index():
        from flask import redirect, session
        if 'teacher_id' in session:
            return redirect('/dashboard')
        else:
            return redirect('/login')

    return app


# === Optional: Safe dev server (disable in production) ===
# if __name__ == '__main__':
#     app = create_app()
#     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)