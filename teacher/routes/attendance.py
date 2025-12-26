# teacher/routes/attendance.py
from flask import Blueprint, session, redirect, request
from models import db, Teacher, Student, Attendance
from datetime import datetime
from teacher.ui import render_page

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'teacher_id' not in session:
        return redirect('/login')
    
    teacher = Teacher.query.get(session['teacher_id'])
    if not teacher:
        return redirect('/login')
    
    # Get all classes for this teacher
    students = Student.query.filter_by(teacher_id=teacher.id).all()
    classes = sorted(set(s.class_name for s in students))
    
    if request.method == 'POST':
        # Handle attendance submission
        selected_class = request.form.get('class')
        selected_group = request.form.get('group') if request.form.get('has_groups') == 'true' else None
        date_str = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))
        mark_all_absent = request.form.get('mark_all_absent') == 'true'
        
        if not selected_class:
            return redirect('/attendance')
        
        # Get students for this class (and group if specified)
        query = Student.query.filter_by(
            teacher_id=teacher.id,
            class_name=selected_class
        )
        if selected_group and selected_group != 'all':
            query = query.filter_by(group_name=selected_group)
        class_students = query.order_by(Student.name_full).all()
        
        # Delete existing attendance for this date/class/group
        student_ids = [s.id for s in class_students]
        Attendance.query.filter(
            Attendance.student_id.in_(student_ids),
            Attendance.date == date_str
        ).delete(synchronize_session=False)
        
        if mark_all_absent:
            # Mark ALL students as absent
            for student in class_students:
                att = Attendance(
                    student_id=student.id,
                    date=date_str,
                    present=False
                )
                db.session.add(att)
        else:
            # Get which students were marked present
            present_students = []
            for student in class_students:
                if request.form.get(f'present_{student.id}') == 'on':
                    present_students.append(student.id)
            
            if present_students:
                # Mark selected as present, others as absent
                for student in class_students:
                    att = Attendance(
                        student_id=student.id,
                        date=date_str,
                        present=(student.id in present_students)
                    )
                    db.session.add(att)
            # If no students selected, save NOTHING (all remain unmarked)
        
        db.session.commit()
        # Redirect with group parameter if exists
        url = f'/attendance?class={selected_class}&date={date_str}'
        if selected_group:
            url += f'&group={selected_group}'
        return redirect(url)
    
    # GET request
    selected_class = request.args.get('class')
    selected_group = request.args.get('group')
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # Build class selection form (always shown)
    class_options = ''
    for cls in classes:
        class_options += f'<option value="{cls}">{cls}</option>'
    
    content = f'''
    <!-- Fixed Filter Section -->
    <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); padding: 20px; margin-bottom: 25px;">
        <form id="filterForm" method="GET" style="display: flex; flex-wrap: wrap; gap: 15px; align-items: end;">
            <div style="flex: 1; min-width: 180px;">
                <label style="display: block; margin-bottom: 6px; color: #5f6368; font-weight: 500; font-size: 14px;">القسم:</label>
                <select name="class" id="classSelect" style="width: 100%; padding: 10px 12px; border: 1px solid #dfe0e4; border-radius: 6px; font-size: 15px;">
                    <option value="">-- اختر قسمًا --</option>
                    {class_options}
                </select>
            </div>
            <div style="flex: 1; min-width: 180px;">
                <label style="display: block; margin-bottom: 6px; color: #5f6368; font-weight: 500; font-size: 14px;">الفوج:</label>
                <select name="group" id="groupFilter" style="width: 100%; padding: 10px 12px; border: 1px solid #dfe0e4; border-radius: 6px; font-size: 15px;">
                    <option value="all">جميع الأفواج</option>
                    <option value="فوج 1">فوج 1</option>
                    <option value="فوج 2">فوج 2</option>
                </select>
            </div>
            <div style="flex: 1; min-width: 160px;">
                <label style="display: block; margin-bottom: 6px; color: #5f6368; font-weight: 500; font-size: 14px;">التاريخ:</label>
                <input type="date" name="date" value="{date_str}" 
                       style="width: 100%; padding: 10px 12px; border: 1px solid #dfe0e4; border-radius: 6px; font-size: 15px;">
            </div>
            <div>
                <button type="submit" style="background: #1a73e8; color: white; border: none; padding: 10px 20px; font-size: 15px; border-radius: 6px; font-weight: 600; cursor: pointer; white-space: nowrap;">
                    عرض التلاميذ
                </button>
            </div>
        </form>
    </div>
    '''
    
    # Only show table when class is selected
    if selected_class:
        # Check if this class has groups
        has_groups = Student.query.filter(
            Student.teacher_id == teacher.id,
            Student.class_name == selected_class,
            Student.group_name.isnot(None)
        ).first() is not None
        
        # Get students for this class (and group if specified)
        query = Student.query.filter_by(
            teacher_id=teacher.id,
            class_name=selected_class
        )
        if selected_group and selected_group != 'all':
            query = query.filter_by(group_name=selected_group)
        students = query.order_by(Student.name_full).all()
        
        # Check if user has assigned groups
        class_has_group_assignments = Student.query.filter(
            Student.teacher_id == teacher.id,
            Student.class_name == selected_class,
            Student.group_name.isnot(None)
        ).first() is not None
        
        total_students = len(students)
        
        # Get existing attendance for today
        existing = {}
        if students:
            student_ids = [s.id for s in students]
            records = Attendance.query.filter(
                Attendance.student_id.in_(student_ids),
                Attendance.date == date_str
            ).all()
            existing = {r.student_id: r.present for r in records}
        
        # Calculate stats
        present_count = sum(1 for s in students if existing.get(s.id) is True)
        absent_count = sum(1 for s in students if existing.get(s.id) is False)
        unmarked_count = total_students - present_count - absent_count
        
        # Build student table with numbering
        student_rows = ''
        absent_list = []
        for idx, student in enumerate(students, 1):
            status = existing.get(student.id)
            if status is True:
                status_text = "حاضر"
                status_color = "#28a745"
                checked = 'checked'
            elif status is False:
                status_text = "غائب"
                status_color = "#dc3545"
                checked = ''
                absent_list.append(student.name_full)
            else:
                status_text = "غير مسجل"
                status_color = "#6c757d"
                checked = ''
            
            student_rows += f'''
            <tr>
                <td style="padding: 8px 6px; text-align: center; font-weight: 500; font-size: 13px;">{idx}</td>
                <td style="padding: 8px 6px; text-align: center; width: 30px;">
                    <input type="checkbox" name="present_{student.id}" {checked} style="width: 16px; height: 16px; margin: 0;">
                </td>
                <td style="padding: 8px 6px; font-size: 13px;">
                    {student.name_full}
                    {f'<span style="margin-right: auto; color: #5f6368; font-size: 12px; background: #e8f0fe; padding: 2px 8px; border-radius: 12px; float: left;">{student.group_name}</span>' if student.group_name else ''}
                </td>
                <td style="padding: 8px 6px; text-align: center;">
                    <span style="padding: 3px 8px; border-radius: 14px; font-weight: 600; color: white; background-color: {status_color}; font-size: 11px;">
                        {status_text}
                    </span>
                </td>
            </tr>
            '''
        
        # Build absent list
        absent_html = ''
        if absent_list:
            absent_html = '<div style="margin-top: 15px;"><strong>أسماء الغائبين:</strong><br>'
            absent_html += '<div style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px;">'
            for name in absent_list:
                absent_html += f'<span style="background: #ffebee; color: #c62828; padding: 4px 8px; border-radius: 14px; font-size: 12px;">{name}</span>'
            absent_html += '</div></div>'
        
        # Build statistics with professional coloring
        content += f'''
        <!-- Statistics Section -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin-bottom: 25px;">
            <div style="background: linear-gradient(135deg, #4caf50, #2e7d32); padding: 15px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 13px; opacity: 0.9; margin-bottom: 5px;">الحاضرون</div>
                <div style="font-size: 24px; font-weight: 700;">{present_count}</div>
            </div>
            <div style="background: linear-gradient(135deg, #f44336, #c62828); padding: 15px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 13px; opacity: 0.9; margin-bottom: 5px;">الغائبون</div>
                <div style="font-size: 24px; font-weight: 700;">{absent_count}</div>
            </div>
            <div style="background: linear-gradient(135deg, #2196f3, #0d47a1); padding: 15px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 13px; opacity: 0.9; margin-bottom: 5px;">إجمالي التلاميذ</div>
                <div style="font-size: 24px; font-weight: 700;">{total_students}</div>
            </div>
            <div style="background: linear-gradient(135deg, #ff9800, #e65100); padding: 15px; border-radius: 12px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 13px; opacity: 0.9; margin-bottom: 5px;">نسبة الحضور</div>
                <div style="font-size: 24px; font-weight: 700;">{round((present_count / total_students * 100), 1) if total_students > 0 else 0}%</div>
            </div>
        </div>
        
        {absent_html}
        
        <!-- Students Table -->
        <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden;">
            <div style="padding: 16px; border-bottom: 1px solid #eee; background: #f8f9fa; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <h3 style="color: #1a73e8; margin: 0; font-size: 18px; font-weight: 600;">قائمة التلاميذ - {selected_class} {f'- {selected_group}' if selected_group and selected_group != 'all' else ''}</h3>
                <button type="button" onclick="checkAll()" style="background: #4caf50; color: white; border: none; padding: 6px 12px; font-size: 13px; border-radius: 6px; font-weight: 600; cursor: pointer; white-space: nowrap;">
                    Check All
                </button>
            </div>
            
            {f'<div style="padding: 16px; background: #fff8e6; border: 1px solid #ffe0b2; border-radius: 8px; margin: 15px; text-align: center; color: #d98800; font-weight: 500;">انت لم تقسم تلاميذك بعد. استخدم صفحة "تصنيف الأفواج" لتقسيم التلاميذ إلى أفواج.</div>' if not class_has_group_assignments else ''}
            
            <form method="POST" style="padding: 0;">
                <input type="hidden" name="class" value="{selected_class}">
                <input type="hidden" name="date" value="{date_str}">
                <input type="hidden" name="has_groups" value="{'true' if has_groups else 'false'}">
                {f'<input type="hidden" name="group" value="{selected_group}">' if selected_group else ''}
                
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; min-width: 500px;">
                        <thead>
                            <tr style="background: #f8f9fa;">
                                <th style="padding: 10px 8px; text-align: center; font-weight: 600; color: #5f6368; font-size: 13px; width: 40px;">#</th>
                                <th style="padding: 10px 8px; text-align: center; font-weight: 600; color: #5f6368; font-size: 13px; width: 40px;"></th>
                                <th style="padding: 10px 8px; text-align: right; font-weight: 600; color: #5f6368; font-size: 13px;">الاسم الكامل</th>
                                <th style="padding: 10px 8px; text-align: center; font-weight: 600; color: #5f6368; font-size: 13px; width: 90px;">الحالة</th>
                            </tr>
                        </thead>
                        <tbody>
                            {student_rows if student_rows else '<tr><td colspan="4" style="padding: 25px; text-align: center; color: #5f6368; font-size: 14px;">لا توجد بيانات تلاميذ لهذا القسم</td></tr>'}
                        </tbody>
                    </table>
                </div>
                
                <div style="padding: 16px; border-top: 1px solid #eee; background: white; display: flex; gap: 10px;">
                    <button type="submit" name="mark_all_absent" value="false" style="background: #1a73e8; color: white; border: none; padding: 10px 16px; font-size: 15px; border-radius: 6px; font-weight: 600; cursor: pointer; flex: 1;">
                        حفظ الحضور
                    </button>
                    <button type="submit" name="mark_all_absent" value="true" style="background: #f44336; color: white; border: none; padding: 10px 16px; font-size: 15px; border-radius: 6px; font-weight: 600; cursor: pointer; flex: 1;">
                        تسجيل كل الغياب
                    </button>
                </div>
            </form>
        </div>
        
        <script>
            function checkAll() {{
                const checkboxes = document.querySelectorAll('input[type="checkbox"][name^="present_"]');
                const allChecked = Array.from(checkboxes).every(cb => cb.checked);
                checkboxes.forEach(cb => cb.checked = !allChecked);
            }}
            
            // Set initial values
            document.addEventListener('DOMContentLoaded', function() {{
                {'document.getElementById("classSelect").value = "' + selected_class + '";' if selected_class else ''}
                {'document.getElementById("groupFilter").value = "' + selected_group + '";' if selected_group else ''}
            }});
        </script>
        '''
    else:
        # Show empty state message
        content += '''
        <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); padding: 30px; text-align: center; margin-top: 20px;">
            <div style="color: #5f6368; font-size: 16px; font-weight: 500;">
                ⬆️ يرجى اختيار قسم من الفلتر أعلاه لعرض التلاميذ
            </div>
        </div>
        '''
    
    return render_page(content, title="تسجيل الحضور", teacher_name=teacher.username, current_page="attendance")