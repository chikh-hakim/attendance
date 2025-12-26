# teacher/routes/admin/teachers.py
from flask import Blueprint, redirect, request, session
from models import db, Teacher, Student, Attendance, ContactMessage
from teacher.ui_admin import render_admin_page

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/teachers')
def teachers_list():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    # Get all teachers
    teachers = Teacher.query.order_by(Teacher.username).all()
    
    # Build teachers list
    teachers_html = ''
    for teacher in teachers:
        teachers_html += f'''
        <div style="background: white; border-radius: 10px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h3 style="margin: 0; font-size: 18px; color: #1a73e8; cursor: pointer;" 
                        onclick="viewTeacher({teacher.id})">
                        {teacher.username}
                    </h3>
                    <p style="color: #5f6368; margin: 6px 0 0; font-size: 14px;">{teacher.email}</p>
                    <p style="color: #5f6368; margin: 4px 0 0; font-size: 14px;">المادة: {teacher.subject}</p>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <button onclick="viewTeacher({teacher.id})" 
                            style="background: #e8f0fe; color: #1a73e8; border: 1px solid #1a73e8; padding: 6px 12px; border-radius: 6px; font-size: 13px; cursor: pointer;">
                        عرض التفاصيل
                    </button>
                    <button onclick="deleteTeacher({teacher.id}, '{teacher.username}')" 
                            style="background: #ffebee; color: #d93025; border: 1px solid #d93025; padding: 6px 12px; border-radius: 6px; font-size: 13px; cursor: pointer;">
                        حذف الحساب
                    </button>
                </div>
            </div>
        </div>
        '''
    
    # ✅ 100% SAFE: Define empty state as plain string (outside f-string context)
    if teachers_html:
        display_html = teachers_html
    else:
        display_html = '''
    <div style="background: white; border-radius: 10px; padding: 40px; text-align: center; border: 1px solid #e0e0e0;">
        <div style="font-size: 18px; color: #5f6368;">لا يوجد مدرسين مسجلين بعد</div>
    </div>
        '''

    content = f'''
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 10px;">
        <h2 style="margin: 0; color: #1a73e8; font-size: 22px;">جميع المدرسين ({len(teachers)})</h2>
        <div style="background: #f8f9fa; padding: 8px 16px; border-radius: 20px; font-size: 14px; color: #5f6368;">
            انقر على اسم المدرس لعرض التفاصيل
        </div>
    </div>
    
    {display_html}
    
    <script>
        function viewTeacher(teacherId) {{
            window.location.href = `/admin/teachers/${{teacherId}}`;
        }}
        
        function deleteTeacher(teacherId, username) {{
            if (confirm(`⚠️ هل أنت متأكد من حذف حساب المدرس "${{username}}"؟\\nسيتم حذف جميع بياناته نهائياً!`)) {{
                window.location.href = `/admin/teachers/delete/${{teacherId}}`;
            }}
        }}
    </script>
    '''
    
    return render_admin_page(content, title="إدارة المدرسين", active_page="teachers")

@teachers_bp.route('/teachers/<int:teacher_id>')
def teacher_details(teacher_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    teacher = Teacher.query.get_or_404(teacher_id)
    
    # Get counts
    student_count = Student.query.filter_by(teacher_id=teacher.id).count()
    attendance_count = db.session.query(db.func.count(db.func.distinct(Attendance.date))) \
    .join(Student) \
    .filter(Student.teacher_id == teacher.id) \
    .scalar() or 0
    message_count = ContactMessage.query.filter(
        ContactMessage.email == teacher.email
    ).count()
    
    content = f'''
    <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); padding: 24px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; flex-wrap: wrap; gap: 20px;">
            <div>
                <h2 style="color: #1a73e8; margin: 0; font-size: 24px;">{teacher.username}</h2>
                <p style="color: #5f6368; margin: 8px 0 0; font-size: 15px;">{teacher.email}</p>
                <p style="color: #5f6368; margin: 4px 0 0; font-size: 15px;">المادة: {teacher.subject}</p>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <button onclick="window.location.href='/admin/teachers'" 
                        style="background: #f1f3f4; color: #5f6368; border: 1px solid #dadce0; padding: 8px 16px; border-radius: 6px; font-size: 14px; cursor: pointer;">
                    ← العودة إلى القائمة
                </button>
                <button onclick="deleteTeacher({teacher.id}, '{teacher.username}')" 
                        style="background: #d93025; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-size: 14px; cursor: pointer; font-weight: 500;">
                    حذف الحساب
                </button>
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px; margin-bottom: 24px;">
            <div style="background: #e8f0fe; padding: 16px; border-radius: 10px; text-align: center; border: 1px solid #bfdbfe;">
                <div style="font-size: 13px; color: #1a73e8; margin-bottom: 6px;">التلاميذ</div>
                <div style="font-size: 22px; font-weight: 700; color: #1a73e8;">{student_count}</div>
            </div>
            <div style="background: #e6f4ea; padding: 16px; border-radius: 10px; text-align: center; border: 1px solid #b9e8c9;">
                <div style="font-size: 13px; color: #137333; margin-bottom: 6px;">سجلات الحضور</div>
                <div style="font-size: 22px; font-weight: 700; color: #137333;">{attendance_count}</div>
            </div>
            <div style="background: #fef7e6; padding: 16px; border-radius: 10px; text-align: center; border: 1px solid #ffe8b3;">
                <div style="font-size: 13px; color: #d98800; margin-bottom: 6px;">الرسائل</div>
                <div style="font-size: 22px; font-weight: 700; color: #d98800;">{message_count}</div>
            </div>
        </div>
        
        <h3 style="color: #1a73e8; margin: 24px 0 16px; font-size: 18px;">معلومات الحساب</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
            <div style="background: #f8f9fa; padding: 16px; border-radius: 10px;">
                <div style="font-weight: 600; color: #5f6368; margin-bottom: 8px;">اسم المستخدم</div>
                <div style="font-size: 16px; color: #24292e;">{teacher.username}</div>
            </div>
            <div style="background: #f8f9fa; padding: 16px; border-radius: 10px;">
                <div style="font-weight: 600; color: #5f6368; margin-bottom: 8px;">البريد الإلكتروني</div>
                <div style="font-size: 16px; color: #24292e;">{teacher.email}</div>
            </div>
            <div style="background: #f8f9fa; padding: 16px; border-radius: 10px;">
                <div style="font-weight: 600; color: #5f6368; margin-bottom: 8px;">المادة</div>
                <div style="font-size: 16px; color: #24292e;">{teacher.subject}</div>
            </div>
          <div style="background: #f8f9fa; padding: 16px; border-radius: 10px;">
    <div style="font-weight: 600; color: #5f6368; margin-bottom: 8px;">تاريخ التسجيل</div>
    <div style="font-size: 16px; color: #24292e;">{teacher.created_at.strftime('%Y-%m-%d') if teacher.created_at else 'غير معروف'}</div>
</div>
        </div>
    </div>
    
    <script>
        function deleteTeacher(teacherId, username) {{
            if (confirm(`⚠️ هل أنت متأكد من حذف حساب المدرس "${{username}}"؟\\nسيتم حذف جميع بياناته نهائياً!`)) {{
                window.location.href = `/admin/teachers/delete/${{teacherId}}`;
            }}
        }}
    </script>
    '''
    
    return render_admin_page(content, title=f"تفاصيل المدرس: {teacher.username}", active_page="teachers")

@teachers_bp.route('/teachers/delete/<int:teacher_id>')
def delete_teacher(teacher_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    teacher = Teacher.query.get_or_404(teacher_id)
    
    # Get teacher's email for message deletion
    teacher_email = teacher.email
    
    # Delete related data in correct order (foreign key constraints)
    # 1. Delete attendance records
    student_ids = [s.id for s in Student.query.filter_by(teacher_id=teacher.id).all()]
    if student_ids:
        Attendance.query.filter(Attendance.student_id.in_(student_ids)).delete(synchronize_session=False)
    
    # 2. Delete students
    Student.query.filter_by(teacher_id=teacher.id).delete()
    
    # 3. Delete contact messages
    ContactMessage.query.filter_by(email=teacher_email).delete()
    
    # 4. Delete teacher
    db.session.delete(teacher)
    db.session.commit()
    
    return redirect('/admin/teachers')