# teacher/routes/groups.py
from flask import Blueprint, session, redirect, request
from models import db, Teacher, Student
from teacher.ui import render_page

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/groups', methods=['GET', 'POST'])
def groups():
    if 'teacher_id' not in session:
        return redirect('/login')
    
    teacher = Teacher.query.get(session['teacher_id'])
    if not teacher:
        return redirect('/login')
    
    # Get all classes for this teacher
    students = Student.query.filter_by(teacher_id=teacher.id).all()
    classes = sorted(set(s.class_name for s in students))
    
    if request.method == 'POST':
        selected_class = request.form.get('class')
        action = request.form.get('action')
        
        if not selected_class:
            return redirect('/groups')
        
        # Get students for this class
        class_students = Student.query.filter_by(
            teacher_id=teacher.id,
            class_name=selected_class
        ).all()
        
        if action == 'remove_all':
            # Remove all groups for this class
            for student in class_students:
                student.group_name = None
        else:
            # Update groups
            for student in class_students:
                group = request.form.get(f'group_{student.id}')
                if group in ['فوج 1', 'فوج 2']:
                    student.group_name = group
                else:
                    student.group_name = None
        
        db.session.commit()
        return redirect(f'/groups?class={selected_class}')
    
    # GET request
    selected_class = request.args.get('class')
    
    # Build class selection form
    class_options = ''
    for cls in classes:
        class_options += f'<option value="{cls}">{cls}</option>'
    
    content = f'''
    <!-- Fixed Filter Section -->
    <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); padding: 20px; margin-bottom: 25px;">
        <form method="GET" style="display: flex; flex-wrap: wrap; gap: 15px; align-items: end;">
            <div style="flex: 1; min-width: 200px;">
                <label style="display: block; margin-bottom: 6px; color: #5f6368; font-weight: 500; font-size: 14px;">القسم:</label>
                <select name="class" style="width: 100%; padding: 10px 12px; border: 1px solid #dfe0e4; border-radius: 6px; font-size: 15px;">
                    <option value="">-- اختر قسمًا --</option>
                    {class_options}
                </select>
            </div>
            <div>
                <button type="submit" style="background: #1a73e8; color: white; border: none; padding: 10px 20px; font-size: 15px; border-radius: 6px; font-weight: 600; cursor: pointer; white-space: nowrap;">
                    عرض التلاميذ
                </button>
            </div>
        </form>
    </div>
    '''
    
    if selected_class:
        # Get students for this class
        students = Student.query.filter_by(
            teacher_id=teacher.id,
            class_name=selected_class
        ).order_by(Student.name_full).all()
        
        # Calculate group statistics
        group1_count = sum(1 for s in students if s.group_name == 'فوج 1')
        group2_count = sum(1 for s in students if s.group_name == 'فوج 2')
        no_group_count = len(students) - group1_count - group2_count
        
        # Build student table
        student_rows = ''
        for student in students:
            group1_checked = 'checked' if student.group_name == 'فوج 1' else ''
            group2_checked = 'checked' if student.group_name == 'فوج 2' else ''
            
            # Set row color based on group
            if student.group_name == 'فوج 1':
                row_color = '#e8f5e9'  # Light green
            elif student.group_name == 'فوج 2':
                row_color = '#ffebee'  # Light red
            else:
                row_color = 'white'    # No group
            
            student_rows += f'''
            <tr style="background-color: {row_color};">
                <td style="padding: 7px 5px;  text-align: center; font-size: 14px;">{student.name_full}</td>
                <td style="padding: 7px 5px; text-align: center; width: 80px;">
                    <label style="display: flex; flex-direction: column; align-items: center; cursor: pointer;">
                        <input type="radio" name="group_{student.id}" value="فوج 1" {group1_checked} 
                               style="width: 16px; height: 16px; margin-bottom: 4px;" 
                               onclick="handleRadioClick(this, 'group_{student.id}')">
                        <span style="font-size: 11px; color: #2e7d32;">فوج 1</span>
                    </label>
                </td>
                <td style="padding: 7px 5px; text-align: center; width: 80px;">
                    <label style="display: flex; flex-direction: column; align-items: center; cursor: pointer;">
                        <input type="radio" name="group_{student.id}" value="فوج 2" {group2_checked} 
                               style="width: 16px; height: 16px; margin-bottom: 4px;" 
                               onclick="handleRadioClick(this, 'group_{student.id}')">
                        <span style="font-size: 11px; color: #c62828;">فوج 2</span>
                    </label>
                </td>
                <td style="padding: 7px 5px; text-align: center; width: 80px;">
                    <label style="display: flex; flex-direction: column; align-items: center; cursor: pointer;">
                        <input type="radio" name="group_{student.id}" value="none" 
                               {'checked' if not student.group_name else ''} 
                               style="width: 16px; height: 16px; margin-bottom: 4px;" 
                               onclick="handleRadioClick(this, 'group_{student.id}')">
                        <span style="font-size: 11px; color: #5f6368;">بدون فوج</span>
                    </label>
                </td>
            </tr>
            '''
        
       # teacher/routes/groups.py (updated section only)

        content += f'''
        <!-- Statistics Section -->
       <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; margin-bottom: 20px; font-size: 12px;">
    <!-- فوج 1 -->
    <div style="background: linear-gradient(135deg, #4caf50, #2e7d32); padding: 12px; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 13px; opacity: 0.9; margin-bottom: 6px; font-weight: 600;">فوج 1</div>
        <div style="font-weight: 800; font-size: 20px;">{group1_count}</div>
    </div>
    
    <!-- فوج 2 -->
    <div style="background: linear-gradient(135deg, #f44336, #c62828); padding: 12px; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 13px; opacity: 0.9; margin-bottom: 6px; font-weight: 600;">فوج 2</div>
        <div style="font-weight: 800; font-size: 20px;">{group2_count}</div>
    </div>
    
    <!-- بدون فوج -->
    <div style="background: linear-gradient(135deg, #ff9800, #e65100); padding: 12px; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 13px; opacity: 0.9; margin-bottom: 6px; font-weight: 600;">بدون فوج</div>
        <div style="font-weight: 800; font-size: 20px;">{no_group_count}</div>
    </div>
    
    <!-- الإجمالي -->
    <div style="background: linear-gradient(135deg, #2196f3, #0d47a1); padding: 12px; border-radius: 10px; text-align: center; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 13px; opacity: 0.9; margin-bottom: 6px; font-weight: 600;">الإجمالي</div>
        <div style="font-weight: 800; font-size: 20px;">{len(students)}</div>
    </div>
</div>
        
        <!-- Students Table -->
        <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; margin-bottom: 20px;">
            <div style="padding: 14px; border-bottom: 1px solid #eee; background: #f8f9fa;">
                <h3 style="color: #1a73e8; margin: 0; font-size: 16px; font-weight: 600;">تصنيف التلاميذ - {selected_class}</h3>
            </div>
            
            <form method="POST" style="padding: 0;">
                <input type="hidden" name="class" value="{selected_class}">
                
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; min-width: 400px;">
                        <thead>
                            <tr style="background: #f8f9fa;">
                                <th style="padding: 8px 6px;  text-align: center; font-weight: 500; color: #5f6368; font-size: 14px;">الاسم الكامل</th>
                                <th  style="padding: 8px 6px; text-align: center; font-weight: 600; color: #5f6368; font-size: 14px; width: 60px;">فوج 1</th>
                                <th style="padding: 8px 6px; text-align: center; font-weight: 600; color: #5f6368; font-size: 14px; width: 60px;">فوج 2</th>
                                <th style="padding: 8px 6px; text-align: center; font-weight: 600; color: #5f6368; font-size: 14px; width: 70px;">بدون فوج</th>
                            </tr>
                        </thead>
                        <tbody>
                            {student_rows if student_rows else '<tr><td colspan="4" style="padding: 20px; text-align: center; color: #5f6368; font-size: 13px;">لا توجد بيانات تلاميذ لهذا القسم</td></tr>'}
                        </tbody>
                    </table>
                </div>
                
                <div style="padding: 14px; border-top: 1px solid #eee; background: white; display: flex; gap: 8px; flex-wrap: wrap;">
                    <button type="submit" name="action" value="save" style="background: #1a73e8; color: white; border: none; padding: 8px 16px; font-size: 14px; border-radius: 6px; font-weight: 600; cursor: pointer; flex: 1; min-width: 120px;">
                        حفظ التصنيف
                    </button>
                    <button type="submit" name="action" value="remove_all" style="background: #f44336; color: white; border: none; padding: 8px 16px; font-size: 14px; border-radius: 6px; font-weight: 600; cursor: pointer; flex: 1; min-width: 120px;">
                        إزالة الأفواج
                    </button>
                </div>
            </form>
        </div>
        
        <script>
            function handleRadioClick(clickedRadio, groupName) {{
                const radios = document.querySelectorAll(`input[name="${{groupName}}"]`);
                radios.forEach(radio => radio.checked = (radio === clickedRadio));
            }}
        </script>
        '''
    else:
        content += '''
        <div style="background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); padding: 30px; text-align: center; margin-top: 20px;">
            <div style="color: #5f6368; font-size: 16px; font-weight: 500;">
                ⬆️ يرجى اختيار قسم من الفلتر أعلاه لتصنيف التلاميذ
            </div>
        </div>
        '''
    
    return render_page(content, title="تصنيف الأفواج", teacher_name=teacher.username, current_page="groups")