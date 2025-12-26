# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'algorix-ostad-secret-key-fallback'
    
    # Railway auto-provides DATABASE_URL for PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Improve connection stability
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres"):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 300,
        }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False