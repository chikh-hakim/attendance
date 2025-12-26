# teacher/routes/contact.py
from flask import Blueprint, session, redirect, request
from models import db, Teacher, ContactMessage
from teacher.ui import render_page

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'teacher_id' not in session:
        return redirect('/login')
    
    teacher = Teacher.query.get(session['teacher_id'])
    if not teacher:
        return redirect('/login')
    
    # Auto-filled fields from session
    sender_name = f"{teacher.username} ({teacher.subject})"
    sender_email = teacher.email
    
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validation
        valid_subjects = ['مشكلة تقنية', 'طلب مساعدة', 'اقتراح تحسين', 'أخرى']
        if not subject or subject not in valid_subjects:
            error = "يرجى اختيار موضوع صالح."
        elif len(message) < 10:
            error = "الرسالة يجب أن تحتوي على 10 أحرف على الأقل."
        else:
            # Save to database using your existing model WITH subject
            contact_msg = ContactMessage(
                name=sender_name,
                email=sender_email,
                subject=subject,  # ← Now properly included
                message=message
            )
            db.session.add(contact_msg)
            db.session.commit()
            success = "✅ تم إرسال رسالتك بنجاح! سيتم الرد عليك قريبًا."
        
        return render_page(
            build_form(sender_name, sender_email, subject, message, error if 'error' in locals() else None, success if 'success' in locals() else None),
            title="اتصل بالمسؤول",
            teacher_name=teacher.username,
            current_page="contact"
        )
    
    return render_page(
        build_form(sender_name, sender_email),
        title="اتصل بالمسؤول",
        teacher_name=teacher.username,
        current_page="contact"
    )

def build_form(sender_name="", sender_email="", selected_subject="", message="", error=None, success=None):
    subjects = [
        ("", "-- اختر الموضوع --"),
        ("مشكلة تقنية", "مشكلة تقنية"),
        ("طلب مساعدة", "طلب مساعدة"),
        ("اقتراح تحسين", "اقتراح تحسين"),
        ("أخرى", "أخرى")
    ]
    
    subject_options = ""
    for value, label in subjects:
        selected = 'selected' if value == selected_subject else ''
        subject_options += f'<option value="{value}" {selected}>{label}</option>'
    
    error_html = f'<div style="background: #fce8e6; color: #c5221f; padding: 12px; border-radius: 8px; margin-bottom: 15px; text-align: center; font-weight: 500;">{error}</div>' if error else ''
    success_html = f'<div style="background: #e6f4ea; color: #137333; padding: 12px; border-radius: 8px; margin-bottom: 15px; text-align: center; font-weight: 500;">{success}</div>' if success else ''
    
    return f'''
    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); padding: 25px;">
        <h1 style="color: #1a73e8; text-align: center; margin: 0 0 25px; font-size: 22px; font-weight: 600;">اتصل بالمسؤول</h1>
        
        {error_html}
        {success_html}
        
        <form method="POST">
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; color: #5f6368; font-weight: 500;">الاسم:</label>
                <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; font-weight: 500; color: #24292e;">{sender_name}</div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; color: #5f6368; font-weight: 500;">البريد الإلكتروني:</label>
                <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; font-weight: 500; color: #24292e;">{sender_email}</div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; color: #5f6368; font-weight: 500;">الموضوع:</label>
                <select name="subject" required style="width: 100%; padding: 12px; border: 1px solid #dfe0e4; border-radius: 8px; font-size: 16px; background: white;">
                    {subject_options}
                </select>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; margin-bottom: 8px; color: #5f6368; font-weight: 500;">الرسالة:</label>
                <textarea name="message" required minlength="10" 
                          style="width: 100%; padding: 12px; border: 1px solid #dfe0e4; border-radius: 8px; font-size: 15px; min-height: 150px; resize: vertical;"
                          placeholder="اكتب رسالتك هنا (10 أحرف على الأقل)...">{message}</textarea>
            </div>
            
            <button type="submit" style="background: #1a73e8; color: white; border: none; padding: 12px; font-size: 16px; border-radius: 8px; font-weight: 600; cursor: pointer; width: 100%;">
                إرسال الرسالة
            </button>
        </form>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #5f6368; font-size: 14px;">
            <p>سيتم الرد على رسالتك خلال 24-48 ساعة.</p>
        </div>
    </div>
    '''