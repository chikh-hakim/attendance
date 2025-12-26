# teacher/routes/statistics.py
from flask import Blueprint, session, redirect, request
from datetime import datetime, timedelta, date
from sqlalchemy import func
from models import db, Teacher, Student, Attendance

statistics_bp = Blueprint('statistics', __name__)

def get_today_range():
    today = date.today()
    return today, today
def get_week_range():
    today = date.today()
    start = today - timedelta(days=today.weekday())  # الاثنين
    end = start + timedelta(days=6)  # الأحد
    return start, end
def get_month_range():
    today = date.today()
    start = today.replace(day=1)
    next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    end = next_month - timedelta(days=1)
    return start, end

@statistics_bp.route('/statistics', methods=['GET'])
def index():
    teacher_id = session.get('teacher_id')
    if not teacher_id:
        return redirect('/login')
    
    teacher = Teacher.query.get(teacher_id)
    if not teacher:
        session.clear()
        return redirect('/login')


        # --- تحديد النطاق الزمني ---
    period = request.args.get('period')
    custom_start = request.args.get('start')
    custom_end = request.args.get('end')
    selected_day = request.args.get('day')
    selected_month = request.args.get('month')

    start_date = None
    end_date = None

    if selected_day:
        start_date = end_date = datetime.strptime(selected_day, '%Y-%m-%d').date()
    elif selected_month:
        y, m = map(int, selected_month.split('-'))
        start_date = date(y, m, 1)
        next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        end_date = next_month - timedelta(days=1)
    elif custom_start and custom_end:
        start_date = datetime.strptime(custom_start, '%Y-%m-%d').date()
        end_date = datetime.strptime(custom_end, '%Y-%m-%d').date()
    elif period == 'today':
        start_date, end_date = get_today_range()
    elif period == 'week':
        start_date, end_date = get_week_range()  # ← جديد
    elif period == 'month':
        start_date, end_date = get_month_range()
    else:
        # الافتراضي: هذا اليوم
        start_date, end_date = get_today_range()
        period = 'today'

    date_filter = (Attendance.date >= start_date) & (Attendance.date <= end_date)

    total_students = Student.query.filter_by(teacher_id=teacher_id).count()

    if total_students == 0:
        content = '''
        <style>.empty-state { text-align: center; color: #888; margin: 40px 0; font-size: 16px; }</style>
        <h1 style="text-align: center; color: #0056b3; margin: 10px 0 25px;">إحصائيات الغياب</h1>
        <p class="empty-state">لا توجد بيانات. يرجى إضافة تلاميذ أولاً.</p>
        '''
        from ui import render_page
        return render_page(content, title="إحصائيات الغياب", teacher_name=teacher.username, current_page="statistics")

    # --- حساب الإحصائيات ---
    marked_dates = db.session.query(Attendance.date).join(Student).filter(
        Student.teacher_id == teacher_id,
        date_filter
    ).distinct().count()

    total_absences = Attendance.query.join(Student).filter(
        Student.teacher_id == teacher_id,
        Attendance.present == False,
        date_filter
    ).count()

    total_present = Attendance.query.join(Student).filter(
        Student.teacher_id == teacher_id,
        Attendance.present == True,
        date_filter
    ).count()

    total_records = total_present + total_absences  # = marked_dates * total_students (نظريًا)
    attendance_rate = round((total_present / total_records) * 100, 1) if total_records > 0 else 0

    # --- أكثر التلاميذ غياباً ---
    absent_counts = db.session.query(
        Student.id,
        Student.name_full,
        Student.class_name,
        func.count(Attendance.id).label('absent_count')
    ).join(Attendance).filter(
        Student.teacher_id == teacher_id,
        Attendance.present == False,
        date_filter
    ).group_by(Student.id, Student.name_full, Student.class_name)\
     .order_by(func.count(Attendance.id).desc())\
     .limit(10).all()

    # === CSS مدمج (نظيف ومنظم) ===
    inline_style = '''
    <style>
    .filter-section {
        background: white;
        border-radius: 10px;
        padding: 16px;
        margin: 16px 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }
    .filter-title {
        font-weight: 700;
        color: #0056b3;
        margin: 0 0 12px;
        font-size: 16px;
        text-align: right;
    }
    .period-selector {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        justify-content: center;
        margin-top: 8px;
    }
    .period-selector label {
        display: flex;
        align-items: center;
        gap: 6px;
        font-weight: 500;
        color: #5f6368;
        cursor: pointer;
        padding: 6px 12px;
        border-radius: 8px;
        background: #f8f9fa;
        transition: background 0.2s;
    }
    .period-selector input[type="radio"] {
        margin: 0;
    }
    .period-selector label:hover {
        background: #e8f0fe;
        color: #1a73e8;
    }

    .advanced-form {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-top: 12px;
    }
    .form-group {
        display: flex;
        flex-direction: column;
    }
    .form-group label {
        font-weight: 600;
        margin-bottom: 6px;
        color: #24292e;
        text-align: right;
    }
    .form-group input {
        padding: 8px 10px;
        border: 1px solid #ddd;
        border-radius: 6px;
        direction: ltr;
        text-align: center;
    }
    .form-submit {
        grid-column: span 2;
        text-align: center;
        margin-top: 8px;
    }
    .form-submit button {
        background: #1a73e8;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
    }

    /* Stats */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 16px;
        margin: 24px 0 32px;
    }
    .stat-card {
        background: white;
        padding: 16px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        text-align: center;
    }
    .stat-label {
        font-size: 14px;
        color: #5f6368;
        margin-bottom: 6px;
    }
    .stat-value {
        font-size: 22px;
        font-weight: 700;
        color: #24292e;
    }

    /* Table */
    .table-container {
        overflow-x: auto;
        width: 100%;
        margin-top: 16px;
    }
    .students-table {
        width: 100%;
        border-collapse: collapse;
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .students-table th,
    .students-table td {
        padding: 12px 14px;
        text-align: right;
        border-bottom: 1px solid #eee;
    }
    .students-table th {
        background-color: #f1f3f4;
        font-weight: 600;
        color: #24292e;
        font-size: 14px;
    }

    /* Mobile */
    @media (max-width: 600px) {
        .advanced-form {
            grid-template-columns: 1fr;
        }
        .stat-value { font-size: 18px; }
        .students-table th,
        .students-table td { padding: 10px 8px; font-size: 13px; }
        .period-selector { flex-direction: column; align-items: flex-start; }
    }
    </style>
    '''

    # === JavaScript مدمج ===
    inline_script = '''
    <script>
    function toggleAdvanced() {
        const section = document.getElementById('advancedSection');
        const button = document.getElementById('toggleBtn');
        if (section.style.display === 'none') {
            section.style.display = 'block';
            button.textContent = 'إخفاء الفلتر المتقدم';
        } else {
            section.style.display = 'none';
            button.textContent = 'عرض الفلتر المتقدم';
        }
    }
    </script>
    '''

    # === HTML: الاختصارات + الفلتر المتقدم ===
    period_selector = f'''
    <div class="filter-section">
        <div class="filter-title">اختيار سريع</div>
     <div class="period-selector">
    <label><input type="radio" name="period" value="today" {"checked" if period == "today" and not (selected_day or selected_month or (custom_start and custom_end)) else ""} onchange="location.href='/statistics?period=today'"> هذا اليوم</label>
    <label><input type="radio" name="period" value="week" {"checked" if period == "week" and not (selected_day or selected_month or (custom_start and custom_end)) else ""} onchange="location.href='/statistics?period=week'"> هذا الأسبوع</label>
    <label><input type="radio" name="period" value="month" {"checked" if period == "month" and not (selected_day or selected_month or (custom_start and custom_end)) else ""} onchange="location.href='/statistics?period=month'"> هذا الشهر</label>
</div>
        <button type="button" id="toggleBtn" onclick="toggleAdvanced()" style="margin-top: 16px; background: #e8f0fe; color: #1a73e8; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">
            عرض الفلتر المتقدم
        </button>
    </div>

    <div class="filter-section" id="advancedSection" style="display: none;">
        <div class="filter-title">فلتر متقدم</div>
        <form method="GET" class="advanced-form">
            <div class="form-group">
                <label>يوم معيّن</label>
                <input type="date" name="day" value="{selected_day or ''}">
            </div>
            <div class="form-group">
                <label>شهر معيّن</label>
                <input type="month" name="month" value="{selected_month or ''}">
            </div>
            <div class="form-group">
                <label>من تاريخ</label>
                <input type="date" name="start" value="{custom_start or ''}">
            </div>
            <div class="form-group">
                <label>إلى تاريخ</label>
                <input type="date" name="end" value="{custom_end or ''}">
            </div>
            <div class="form-submit">
                <button type="submit">تطبيق الفلتر</button>
            </div>
        </form>
    </div>
    '''

    # === الإحصائيات الجديدة (كما طلبت) ===
    stats_html = f'''
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-label">عدد الحصص المسجلة</div>
            <div class="stat-value">{marked_dates}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">عدد الحضور الكلي</div>
            <div class="stat-value" style="color: #28a745;">{total_present}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">عدد الغياب الكلي</div>
            <div class="stat-value" style="color: #d93025;">{total_absences}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">نسبة الحضور</div>
            <div class="stat-value" style="color: {"#28a745" if attendance_rate >= 80 else "#d93025"};">
                {attendance_rate}%
            </div>
        </div>
    </div>
    '''

    # === جدول أكثر الغائبين ===
    if absent_counts:
        table_rows = ""
        for i, (sid, name_full, cls, count) in enumerate(absent_counts, 1):
            table_rows += f'''
            <tr>
                <td>{i}</td>
                <td>{name_full}</td>
                <td>{cls}</td>
                <td style="color: #d93025; font-weight: 600;">{count}</td>
            </tr>
            '''
        absent_table = f'''
        <h2 style="margin: 24px 0 12px; color: #0056b3; text-align: right;">أكثر التلاميذ غياباً</h2>
        <div class="table-container">
            <table class="students-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>الاسم الكامل</th>
                        <th>القسم</th>
                        <th>عدد الغيابات</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        '''
    else:
        absent_table = '''
        <h2 style="margin: 24px 0 12px; color: #0056b3; text-align: right;">أكثر التلاميذ غياباً</h2>
        <p style="text-align: center; color: #555;">لا توجد حالات غياب في الفترة المحددة.</p>
        '''

    content = f'''
    {inline_style}
    <h1 style="text-align: center; color: #0056b3; margin: 10px 0 20px;">إحصائيات الغياب</h1>
    {period_selector}
    {stats_html}
    {absent_table}
    {inline_script}
    '''

    from ui import render_page
    return render_page(
        content,
        title="إحصائيات الغياب",
        teacher_name=teacher.username,
        current_page="statistics"
    )