# teacher/routes/admin/messages.py
from flask import Blueprint, redirect, request, session
from models import db, ContactMessage
from teacher.ui_admin import render_admin_page
from collections import defaultdict
import urllib.parse

messages_bp = Blueprint('messages', __name__)

def create_gmail_link(email, name, subject="رد على رسالتك"):
    """إنشاء رابط Gmail جاهز للرد — آمن وبدون أخطاء"""
    first_name = name.split()[0] if name else "المستخدم"
    # Use %0A for newlines in URL (Gmail requires encoded newlines)
    body = f"مرحباً {first_name}،%0A%0Aشكراً لتواصلك معنا."
    # ✅ No extra spaces, all parts quoted
    return (
        "https://mail.google.com/mail/?view=cm&fs=1&to=" +
        urllib.parse.quote(email) +
        "&su=" + urllib.parse.quote(subject) +
        "&body=" + urllib.parse.quote(body)
    )

@messages_bp.route('/messages')
def messages_list():
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    all_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    messages_by_email = defaultdict(list)
    for msg in all_messages:
        messages_by_email[msg.email].append(msg)
    
    latest_messages = [msgs[0] for msgs in messages_by_email.values()]
    latest_messages.sort(key=lambda x: x.created_at, reverse=True)
    
    messages_html = ''
    for msg in latest_messages:
        date_str = msg.created_at.strftime('%Y-%m-%d %H:%M') if msg.created_at else 'غير معروف'
        total = len(messages_by_email[msg.email])
        gmail_link = create_gmail_link(msg.email, msg.name, msg.subject)
        
        # ✅ SAFE: Use single quotes for onclick attr, double inside → NO BACKSLASH
        view_all_btn = ''
        if total > 1:
            view_all_btn = f'''<button onclick='viewAllFrom("{msg.email}")'
                                style="background: #f1f3f4; color: #5f6368; border: 1px solid #dadce0; padding: 6px 12px; border-radius: 8px; font-size: 13px; cursor: pointer;">
                                عرض جميع الرسائل ({total})
                               </button>'''
        
        messages_html += f'''
        <div style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border: 1px solid #eee;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div style="flex: 1; min-width: 220px;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap;">
                        <h3 style="margin: 0; font-size: 17px; color: #1a73e8;">{msg.name}</h3>
                        <a href="{gmail_link}" target="_blank"
                           style="background: #e8f0fe; color: #1a73e8; padding: 3px 10px; border-radius: 20px; font-size: 13px; text-decoration: none; font-weight: 500;">
                            {msg.email}
                        </a>
                    </div>
                    <p style="color: #5f6368; margin: 6px 0; font-size: 14px; font-weight: 600;">{msg.subject}</p>
                    <p style="color: #24292e; margin: 8px 0; font-size: 14px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                        {msg.message}
                    </p>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 8px; min-width: 130px;">
                    <div style="color: #5f6368; font-size: 12px; background: #f8f9fa; padding: 4px 10px; border-radius: 20px;">
                        {date_str}
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px; width: 100%;">
                        <button onclick="viewMessage({msg.id})" 
                                style="background: #1a73e8; color: white; border: none; padding: 6px 12px; border-radius: 8px; font-size: 13px; cursor: pointer; font-weight: 500;">
                            عرض الرسالة
                        </button>
                        {view_all_btn}
                        <button onclick="deleteMessage({msg.id})" 
                                style="background: #ffebee; color: #d93025; border: 1px solid #d93025; padding: 6px 12px; border-radius: 8px; font-size: 13px; cursor: pointer; margin-top: 4px;">
                            حذف
                        </button>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    empty_state = '''
    <div style="background: white; border-radius: 12px; padding: 40px; text-align: center; border: 1px solid #eee; margin-top: 20px;">
        <div style="font-size: 18px; color: #5f6368;">لا توجد رسائل حتى الآن</div>
    </div>
    '''
    
    content = f'''
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
        <div style="background: #f8f9fa; padding: 8px 16px; border-radius: 24px; font-size: 14px; color: #5f6368;">
            أحدث رسالة من كل مستخدم
        </div>
    </div>
    {messages_html if messages_html else empty_state}
    
    <script>
        function viewMessage(id) {{
            window.location.href = "/admin/messages/" + id;
        }}
        function viewAllFrom(email) {{
            window.location.href = "/admin/messages/user/" + encodeURIComponent(email);
        }}
        function deleteMessage(id) {{
            if (confirm("⚠️ هل أنت متأكد من حذف هذه الرسالة؟")) {{
                window.location.href = "/admin/messages/delete/" + id;
            }}
        }}
    </script>
    '''
    
    return render_admin_page(content, title="رسائل الاتصال", active_page="messages")


@messages_bp.route('/messages/user/<email>')
def user_messages(email):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    messages = ContactMessage.query.filter_by(email=email).order_by(ContactMessage.created_at.desc()).all()
    if not messages:
        return redirect('/admin/messages')
    
    name = messages[0].name
    messages_html = ''
    for msg in messages:
        date_str = msg.created_at.strftime('%Y-%m-%d %H:%M') if msg.created_at else 'غير معروف'
        gmail_link = create_gmail_link(msg.email, msg.name, msg.subject)
        
        messages_html += f'''
        <div style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.08); border: 1px solid #eee;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
                <div style="flex: 1; min-width: 220px;">
                    <p style="color: #5f6368; margin: 0 0 6px; font-size: 14px; font-weight: 600;">{msg.subject}</p>
                    <p style="color: #24292e; margin: 8px 0; font-size: 14px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">
                        {msg.message}
                    </p>
                </div>
                <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 8px; min-width: 130px;">
                    <div style="color: #5f6368; font-size: 12px; background: #f8f9fa; padding: 4px 10px; border-radius: 20px;">
                        {date_str}
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button onclick="viewMessage({msg.id})" 
                                style="background: #1a73e8; color: white; border: none; padding: 6px 12px; border-radius: 8px; font-size: 13px; cursor: pointer; font-weight: 500;">
                            عرض
                        </button>
                        <a href="{gmail_link}" target="_blank"
                           style="background: #e8f0fe; color: #1a73e8; border: 1px solid #1a73e8; padding: 6px 12px; border-radius: 8px; font-size: 13px; text-decoration: none; font-weight: 500;">
                            رد
                        </a>
                        <button onclick="deleteMessage({msg.id})" 
                                style="background: #ffebee; color: #d93025; border: 1px solid #d93025; padding: 6px 12px; border-radius: 8px; font-size: 13px; cursor: pointer;">
                            حذف
                        </button>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    content = f'''
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
        <button onclick="window.location.href='/admin/messages'" 
                style="background: #f1f3f4; color: #5f6368; border: 1px solid #dadce0; padding: 8px 16px; border-radius: 8px; font-size: 14px; cursor: pointer;">
            ← العودة إلى القائمة
        </button>
    </div>
    {messages_html}
    
    <script>
        function viewMessage(id) {{
            window.location.href = "/admin/messages/" + id;
        }}
        function deleteMessage(id) {{
            if (confirm("⚠️ هل أنت متأكد من حذف هذه الرسالة؟")) {{
                window.location.href = "/admin/messages/delete/" + id;
            }}
        }}
    </script>
    '''
    
    return render_admin_page(content, title=f"رسائل: {name}", active_page="messages")


@messages_bp.route('/messages/<int:message_id>')
def message_details(message_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    
    msg = ContactMessage.query.get_or_404(message_id)
    date_str = msg.created_at.strftime('%Y-%m-%d %H:%M') if msg.created_at else 'غير معروف'
    gmail_link = create_gmail_link(msg.email, msg.name, msg.subject)
    
    content = f'''
    <div style="max-width: 800px; margin: 0 auto;">
        <div style="background: white; border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
                <div>
                    <p style="color: #5f6368; margin: 8px 0 4px; font-size: 15px;">
                        <strong>{msg.name}</strong>
                    </p>
                    <p style="color: #5f6368; margin: 4px 0; font-size: 14px;">
                        {date_str}
                    </p>
                </div>
                <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                    <a href="{gmail_link}" target="_blank"
                       style="background: #1a73e8; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-size: 14px; text-decoration: none; font-weight: 600;">
                        الرد عبر Gmail
                    </a>
                    <button onclick="window.location.href='/admin/messages'" 
                            style="background: #f1f3f4; color: #5f6368; border: 1px solid #dadce0; padding: 8px 16px; border-radius: 8px; font-size: 14px; cursor: pointer;">
                        ← العودة
                    </button>
                    <button onclick="deleteMessage({msg.id})" 
                            style="background: #d93025; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-size: 14px; cursor: pointer; font-weight: 600;">
                        حذف
                    </button>
                </div>
            </div>
        </div>

        <div style="background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
            <h2 style="color: #1a73e8; margin: 0 0 16px; font-size: 18px; padding-bottom: 10px; border-bottom: 1px solid #eee;">
                معلومات المرسل
            </h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div>
                    <div style="font-weight: 600; color: #5f6368; margin-bottom: 6px; font-size: 14px;">الاسم الكامل</div>
                    <div style="font-size: 16px; color: #24292e;">{msg.name}</div>
                </div>
                <div>
                    <div style="font-weight: 600; color: #5f6368; margin-bottom: 6px; font-size: 14px;">البريد الإلكتروني</div>
                    <a href="{gmail_link}" target="_blank" 
                       style="font-size: 16px; color: #1a73e8; text-decoration: none; font-weight: 600;">
                        {msg.email}
                    </a>
                </div>
                <div>
                    <div style="font-weight: 600; color: #5f6368; margin-bottom: 6px; font-size: 14px;">الموضوع</div>
                    <div style="font-size: 16px; color: #24292e;">{msg.subject}</div>
                </div>
            </div>
        </div>

        <div style="background: white; border-radius: 12px; padding: 24px; margin-top: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
            <h2 style="color: #1a73e8; margin: 0 0 16px; font-size: 18px; padding-bottom: 10px; border-bottom: 1px solid #eee;">
                محتوى الرسالة
            </h2>
            <div style="color: #24292e; line-height: 1.6; white-space: pre-wrap; font-size: 15px;">
                {msg.message}
            </div>
        </div>
    </div>

    <script>
        function deleteMessage(id) {{
            if (confirm("⚠️ هل أنت متأكد من حذف هذه الرسالة؟")) {{
                window.location.href = "/admin/messages/delete/" + id;
            }}
        }}
    </script>
    '''
    
    return render_admin_page(content, title=f"رسالة: {msg.subject}", active_page="messages")


@messages_bp.route('/messages/delete/<int:message_id>')
def delete_message(message_id):
    if not session.get('admin_logged_in'):
        return redirect('/admin/login')
    msg = ContactMessage.query.get_or_404(message_id)
    db.session.delete(msg)
    db.session.commit()
    return redirect('/admin/messages')