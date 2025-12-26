# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime  # ← تأكد من استيراد datetime

db = SQLAlchemy()

class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    
    # الاسم الكامل (اللقب + الاسم)
    name_full = db.Column(db.String(200), nullable=False)
    
    # القسم: مثال "1M1", "3M12", "4M20"
    class_name = db.Column(db.String(20), nullable=False)
    
    # الفوج: "فوج 1", "فوج 2", أو NULL إذا لم يُصنّف الأستاذ
    group_name = db.Column(db.String(20), nullable=True)

    # علاقة للاستخدام في الاستعلامات
    teacher = db.relationship('Teacher', backref=db.backref('students', lazy=True))

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)  # التاريخ (YYYY-MM-DD)
    present = db.Column(db.Boolean, default=False)      # True = حاضر، False = غائب

    # علاقة للتلميذ
    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))

# models.py
class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(100), nullable=False)  # ← تأكد من وجود هذا السطر
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)