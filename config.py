# config.py
import os

class Config:
    # مفتاح سري من متغيرات البيئة (يتم تعيينه في Render)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'algorix-ostad-pro-secret-key-2025'

    # قاعدة بيانات من متغيرات البيئة (Render سيمددها تلقائياً)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # إذا كنت تستخدم PostgreSQL (كما في Render)، أضف هذا الخيار لتجنب تحذير
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres"):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }
    
    # تعطيل تتبع التعديلات لتحسين الأداء
    SQLALCHEMY_TRACK_MODIFICATIONS = False