# teacher/routes/dashboard.py
from flask import Blueprint, session, redirect, request
from collections import defaultdict
from models import db, Teacher, Student, Attendance
from ui import render_page
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
def index():
    teacher_id = session.get('teacher_id')
    if not teacher_id:
        return redirect('/login')

    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        session.clear()
        return redirect('/login')

    # --- حذف البيانات ---
    if request.method == 'POST':
        student_ids = [s.id for s in Student.query.filter_by(teacher_id=teacher_id).all()]
        if student_ids:
            Attendance.query.filter(Attendance.student_id.in_(student_ids)).delete(synchronize_session=False)
        Student.query.filter_by(teacher_id=teacher_id).delete()
        db.session.commit()
        return redirect('/dashboard')

    # --- جلب جميع التلاميذ ---
    all_students = Student.query.filter_by(teacher_id=teacher_id).order_by(Student.name_full).all()
    classes = defaultdict(list)
    for s in all_students:
        classes[s.class_name].append(s)

    # --- معالجة البحث ---
    search_query = request.args.get('q', '').strip()
    selected_class = request.args.get('class_filter', '').strip()
    student_absences = []
    found_student = None

    if search_query:
        query = Student.query.filter(
            Student.teacher_id == teacher_id,
            Student.name_full.ilike(f'%{search_query}%')
        )
        if selected_class:
            query = query.filter(Student.class_name == selected_class)
        found_student = query.first()

        if found_student:
            absences = Attendance.query.filter_by(
                student_id=found_student.id,
                present=False
            ).order_by(Attendance.date.desc()).all()
            student_absences = [a.date.strftime('%Y-%m-%d') for a in absences]

    # === إنشاء datalist للأسماء حسب القسم ===
    datalist_options = ""
    for student in all_students:
        datalist_options += f'<option value="{student.name_full}" data-class="{student.class_name}">'

    # === إنشاء خيارات القسم للـ filter ===
    class_options = '<option value="">جميع الأقسام</option>'
    for cls in sorted(classes.keys()):
        selected = 'selected' if cls == selected_class else ''
        class_options += f'<option value="{cls}" {selected}>{cls}</option>'

    # === CSS مدمج ===
    inline_style = '''
    <style>
    .search-section {
        background: white;
        padding: 18px;
        border-radius: 10px;
        margin: 0 0 24px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        text-align: right;
    }
    .search-section h2 {
        margin: 0 0 12px;
        color: #0056b3;
        font-size: 18px;
    }
    .search-controls {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
        margin-top: 10px;
    }
    .search-controls input,
    .search-controls select,
    .search-controls button {
        padding: 10px 12px;
        border: 1px solid #ccc;
        border-radius: 6px;
        font-size: 15px;
        direction: ltr;
    }
    .search-controls input {
        direction: rtl;
        min-width: 200px;
        flex: 1;
    }
    .search-controls select {
        direction: rtl;
        min-width: 140px;
    }
    .search-controls button {
        background: #1a73e8;
        color: white;
        border: none;
        font-weight: 600;
        cursor: pointer;
        min-width: 100px;
    }
    .search-results {
        margin-top: 16px;
        padding: 12px;
        background: #f8f9fa;
        border-radius: 8px;
        direction: rtl;
    }
   .classes-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 12px;
        margin: 16px 0;
    }

    .class-item {
        background: white;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
    }
    .class-name { font-weight: bold; color: #0056b3; }
    .class-count {
        background: #eef4ff;
        padding: 2px 10px;
        border-radius: 20px;
        font-weight: 600;
    }
    .empty-state {
        text-align: center;
        padding: 40px 20px;
        color: #666;
    }
    .empty-state h3 {
        margin: 0 0 16px;
        color: #0056b3;
    }
    .empty-state a {
        display: inline-block;
        background: #1a73e8;
        color: white;
        text-decoration: none;
        padding: 10px 24px;
        border-radius: 6px;
        font-weight: 600;
        margin-top: 12px;
    }
     @media (min-width: 800px) {
        .classes-grid {
            grid-template-columns: repeat(4, 1fr);
        }
    }

    @media (max-width: 600px) {
         .classes-grid {
            grid-template-columns: 1fr;
        }
        .search-controls {
            flex-direction: column;
        }
        .search-controls input,
        .search-controls select,
        .search-controls button {
            width: 100%;
            min-width: auto;
        }
    }
    </style>
    '''
       # === شريط البحث المُعاد تصميمه بالكامل ===
       # === شريط البحث المُعاد تصميمه (بدون خطأ f-string) ===

    # CSS كـ متغير مستقل (لا يحتوي على f-string)
    search_css = '''
    <style>
    .search-section {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 24px;
    }
    .search-section h2 {
        color: #0056b3;
        font-size: 18px;
        margin: 0 0 16px;
        text-align: right;
    }
    .search-form {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        align-items: flex-end;
    }
    .input-group {
        flex: 1;
        min-width: 220px;
        position: relative;
    }
    .input-group input {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid #ccc;
        border-radius: 8px;
        font-size: 15px;
        direction: rtl;
        text-align: right;
    }
    .filter-group {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
    }
    .filter-group select,
    .filter-group button {
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 15px;
        border: 1px solid #ccc;
        height: fit-content;
    }
    .filter-group select {
        background: white;
        direction: rtl;
        text-align: right;
        min-width: 140px;
    }
    .filter-group button {
        background: #1a73e8;
        color: white;
        border: none;
        font-weight: 600;
        cursor: pointer;
        white-space: nowrap;
    }
    .result-card {
        background: #f9fbfd;
        border: 1px solid #e0e6ed;
        border-radius: 10px;
        overflow: hidden;
    }
    .result-header {
        background: #e6f0fa;
        padding: 14px 16px;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        border-bottom: 1px solid #d0e0f0;
    }
    .class-tag {
        background: #cfe5ff;
        color: #0056b3;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        white-space: nowrap;
    }
    .student-fullname {
        font-weight: 700;
        color: #0056b3;
        font-size: 17px;
        flex: 1;
        text-align: right;
        min-width: 120px;
    }
    .absence-total {
        background: #ffebee;
        color: #d93025;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        white-space: nowrap;
    }
    .result-body {
        padding: 18px 16px 12px;
        text-align: right;
    }
    .dates-label {
        font-weight: 600;
        color: #24292e;
        margin-bottom: 10px;
        font-size: 15px;
    }
    .dates-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: flex-start;
    }
    .date-item {
        background: #fff0f0;
        color: #d93025;
        padding: 5px 11px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 14px;
        border: 1px solid #ffd5d5;
        direction: ltr;
        text-align: center;
    }
    .no-absence {
        color: #28a745;
        font-weight: 600;
        font-size: 15px;
        text-align: center;
        padding: 8px 0;
    }
    @media (max-width: 600px) {
        .search-form {
            flex-direction: column;
            align-items: stretch;
        }
        .filter-group {
            justify-content: center;
        }
        .result-header {
            flex-direction: column;
            align-items: stretch;
        }
        .student-fullname,
        .absence-total {
            text-align: center;
        }
    }
    </style>
    '''

    # HTML بدون CSS داخلي (باستثناء التعبيرات الآمنة)
    search_html = f'''

<div class="platform-intro" style="
    text-align: center;
    margin: 36px auto 30px;
    padding: 24px 34px;
    max-width: 800px;
    background: linear-gradient(135deg, #d4a017, #fbbf24);
    border-radius: 16px;
    box-shadow: 0 6px 20px rgba(212, 160, 23, 0.25);
    font-size: 22px;
    font-weight: 800;
    color: white;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    line-height: 1.45;
    direction: rtl;
    font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
    letter-spacing: -0.3px;
">
    نظام إدارة الغياب الذكي وتحكم كامل ببيانات حضور التلاميذ.
</div>


    <div class="search-section">

        <h2>البحث عن غياب تلميذ</h2>
        <form method="GET" class="search-form">
            <div class="input-group">
                <input type="text"
                       name="q"
                       id="studentSearch"
                       list="studentsList"
                       placeholder="اكتب الاسم الكامل للتلميذ..."
                       value="{search_query}"
                       autocomplete="off">
                <datalist id="studentsList">
                    {datalist_options}
                </datalist>
            </div>
            <div class="filter-group">
                <select name="class_filter">{class_options}</select>
                <button type="submit">بحث</button>
            </div>
        </form>

        {
            '<div class="result-card" style="margin-top: 20px;">'
            '<div style="text-align:center; color:#d93025; padding:16px;">لم يتم العثور على تلميذ بهذا الاسم.</div>'
            '</div>'
            if search_query and not found_student
            else
            f'<div class="result-card" style="margin-top: 20px;">'
            f'<div class="result-header">'
            f'<span class="class-tag">{found_student.class_name}</span>'
            f'<span class="student-fullname">{found_student.name_full}</span>'
            f'<span class="absence-total">الغيابات: {len(student_absences)}</span>'
            f'</div>'
            f'<div class="result-body">'
            f'<div class="dates-label">أيام الغياب:</div>'
            + ('<div class="dates-list">' + ''.join(f'<span class="date-item">{d}</span>' for d in student_absences) + '</div>' if student_absences else '<div class="no-absence">✓ لم يتغيب</div>')
            + '</div>'
            + '</div>'
            if search_query and found_student
            else
            ''
        }
    </div>
    '''

    search_section = search_css + search_html
    # === عرض الأقسام في عمودين ===
    if classes:
        class_items = ""
        for class_name in sorted(classes.keys()):
            count = len(classes[class_name])
            class_items += f'''
            <div class="class-item">
                <span class="class-name">{class_name}</span>
                <span class="class-count">{count} تلميذ</span>
            </div>
            '''
        classes_display = f'''
        <h2 style="margin: 24px 0 12px; color: #0056b3; text-align: right;">الأقسام المسجلة:</h2>
        <div class="classes-grid">
            {class_items}
        </div>
        '''
        delete_btn = '''
        <form method="POST" onsubmit="return confirm('⚠️ هل أنت متأكد؟\\nسيتم حذف جميع بياناتك نهائياً!');" style="text-align: center; margin-top: 24px;">
            <button type="submit" style="background: #ff4d4f; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer;">
                🗑️ حذف جميع البيانات
            </button>
        </form>
        '''
        content = f'{inline_style}{search_section}{classes_display}{delete_btn}'
    else:
        content = f'''
        {inline_style}
        {search_section}
        <div class="empty-state">
            <h3>لم تقم بعد بإضافة أي تلاميذ!</h3>
            <p>يجب عليك إضافة بيانات التلاميذ أولاً لتتمكن من تسجيل الحضور والغياب.</p>
            <a href="/upload">إضافة تلاميذ الآن</a>
        </div>
        '''

    return render_page(
        content,
        title="الرئيسية",
        teacher_name=teacher.username,
        current_page="dashboard"
    )