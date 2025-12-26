# config.py
class Config:
    # مفتاح سري قوي
    SECRET_KEY = 'algorix-ostad-pro-secret-key-2025'

    # إعدادات قاعدة البيانات لـ PythonAnywhere
    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://chikhhakim:ostad1234@'
        'chikhhakim.mysql.pythonanywhere-services.com/'
        'chikhhakim$ostad_db'
    )
    
    # تعطيل تتبع التعديلات لتحسين الأداء
    SQLALCHEMY_TRACK_MODIFICATIONS = False