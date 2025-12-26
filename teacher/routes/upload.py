# teacher/routes/upload.py
import os
import pandas as pd
import re
from flask import Blueprint, request, redirect, session
from werkzeug.utils import secure_filename
from models import db, Teacher, Student
from teacher.ui import render_page

upload_bp = Blueprint('upload', __name__)
def extract_class(text):
    """Extract class like '3M1' from text containing 'الفوج التربوي : ثالثة متوسط 1'"""
    if "أولى" in text:
        level = "1"
    elif "ثانية" in text:
        level = "2"
    elif "ثالثة" in text:
        level = "3"
    elif "رابعة" in text:
        level = "4"
    else:
        return None
    # Find number right after "متوسط"
    match = re.search(r'متوسط\s*(\d+)', text)
    if not match:
        return None

    num_str = match.group(1)
    if num_str.isdigit():
        num = int(num_str)
        if 1 <= num <= 20:  # Valid class number
            return f"{level}M{num}"
    return None

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'teacher_id' not in session:
        return redirect('/login')
    
    teacher = Teacher.query.get(session['teacher_id'])
    if not teacher:
        return redirect('/login')
    
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            content = '''
            <div class="message error" style="padding: 15px; margin: 20px 0; border-radius: 8px; background: #fce8e6; color: #c5221f; border-right: 4px solid #c5221f; text-align: center; font-weight: 500;">
                لم يتم تحديد ملف.
            </div>
            '''
            return render_page(content, title="رفع ملف Excel", teacher_name=teacher.username, current_page="upload")

        filename = secure_filename(file.filename)
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        teacher_id = session['teacher_id']
        processed_sheets = 0
        skipped_sheets = []

        try:
            with pd.ExcelFile(filepath) as xls:
                for sheet in xls.sheet_names:
                    try:
                        class_row = pd.read_excel(
                            xls, 
                            sheet_name=sheet, 
                            header=None, 
                            skiprows=4, 
                            nrows=1
                        )
                        
                        if class_row.empty or class_row.shape[1] == 0:
                            skipped_sheets.append((sheet, "السطر 5 فارغ"))
                            continue

                        full_text = ""
                        found = False
                        for cell in class_row.iloc[0]:
                            if pd.notna(cell):
                                cell_str = str(cell).strip()
                                if "الفوج التربوي" in cell_str:
                                    full_text = cell_str
                                    found = True
                                    break

                        if not found:
                            skipped_sheets.append((sheet, "لا يحتوي على 'الفوج التربوي'"))
                            continue

                        class_name = extract_class(full_text)
                        if not class_name:
                            skipped_sheets.append((sheet, "لا يحتوي على رقم قسم صالح (1-20)"))
                            continue

                        df = pd.read_excel(xls, sheet_name=sheet, skiprows=8)
                        if df.empty:
                            skipped_sheets.append((sheet, "لا يحتوي على تلاميذ"))
                            continue

                        if df.shape[0] > 0 and 'رقم التعريف' in str(df.iloc[0, 0]):
                            df = df.iloc[1:].reset_index(drop=True)
                        df = df.dropna(how='all')
                        if df.empty or df.shape[1] < 3:
                            skipped_sheets.append((sheet, "بيانات التلاميذ غير كافية"))
                            continue

                        Student.query.filter_by(
                            teacher_id=teacher_id, 
                            class_name=class_name
                        ).delete()

                        for _, row in df.iterrows():
                            last_name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ''
                            first_name = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ''
                            if not last_name and not first_name:
                                continue
                            name_full = f"{last_name} {first_name}".strip()
                            if not name_full:
                                continue

                            student = Student(
                                teacher_id=teacher_id,
                                name_full=name_full,
                                class_name=class_name,
                                group_name=None
                            )
                            db.session.add(student)
                        processed_sheets += 1

                    except Exception as e:
                        skipped_sheets.append((sheet, "خطأ في معالجة الورقة"))

            db.session.commit()
            os.remove(filepath)

            content = f'''
            <div class="message success" style="padding: 15px; margin: 20px 0; border-radius: 8px; background: #e6f4ea; color: #137333; border-right: 4px solid #137333; text-align: center; font-weight: 500;">
                تم رفع {processed_sheets} أقسام بنجاح!
            </div>
            '''
            
            if skipped_sheets:
                skipped_html = '''
                <div class="message warning" style="padding: 15px; margin: 20px 0; border-radius: 8px; background: #fffbe6; color: #d48806; border-right: 4px solid #d48806; text-align: center; font-weight: 500;">
                    تم تجاهل بعض الأوراق:
                </div>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; text-align: right; max-height: 200px; overflow-y: auto;">
                '''
                for sheet, reason in skipped_sheets:
                    skipped_html += f'<div style="padding: 6px 0; border-bottom: 1px solid #eee;">• <b>{sheet}</b>: {reason}</div>'
                skipped_html += '</div>'
                content += skipped_html

            return render_page(content, title="رفع ملف Excel", teacher_name=teacher.username, current_page="upload")

        except Exception as e:
            if os.path.exists(filepath):
                try: 
                    os.remove(filepath)
                except: 
                    pass
            content = '''
            <div class="message error" style="padding: 15px; margin: 20px 0; border-radius: 8px; background: #fce8e6; color: #c5221f; border-right: 4px solid #c5221f; text-align: center; font-weight: 500;">
                حدث خطأ أثناء معالجة الملف.
            </div>
            '''
            return render_page(content, title="رفع ملف Excel", teacher_name=teacher.username, current_page="upload")
    # GET request - show upload form
    content = '''
    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); padding: 30px; text-align: center;">
        <h1 style="color: #1a73e8; margin: 0 0 20px; font-size: 24px; font-weight: 600;">رفع ملف Excel</h1>
        
        <form method="post" enctype="multipart/form-data" id="upload-form">
            <div id="drop-area" style="background: #f8f9fa; border: 2px dashed #1a73e8; border-radius: 10px; padding: 30px; margin: 20px 0; cursor: pointer; transition: all 0.3s; position: relative;">
                <div id="file-preview" style="pointer-events: none;">
                    <div style="margin-bottom: 15px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#1a73e8" stroke-width="1.5" style="margin: 0 auto;">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                            <polyline points="17 8 12 3 7 8"></polyline>
                            <line x1="12" y1="3" x2="12" y2="15"></line>
                        </svg>
                    </div>
                    <p style="margin: 0; color: #1a73e8; font-weight: 600; font-size: 18px;">ارفع ملف Excel الذي يحتوي على قائمة التلاميذ</p>
                    <p style="margin: 10px 0 0; color: #5f6368; font-size: 14px;">أو انقر لاختيار الملف</p>
                </div>
                
                <input type="file" id="file-input" name="file" accept=".xlsx,.xls" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; opacity: 0; cursor: pointer;">
            </div>
            
            <button type="submit" id="submit-btn" 
                    style="background: #1a73e8; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 6px; cursor: pointer; font-weight: 600; margin-top: 10px; width: 100%; opacity: 0.6; cursor: not-allowed;"
                    disabled>
                رفع الملف
            </button>
        </form>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; font-size: 14px; color: #5f6368; text-align: right;">
            <p style="margin: 0 0 8px; font-weight: 600;">مثال على سطر 5 في الورقة:</p>
            <p style="margin: 0; padding: 8px; background: white; border-radius: 6px; direction: ltr; font-family: monospace;">
                "الفوج التربوي : ثالثة متوسط 1"
            </p>
        </div>
        
        <div style="margin-top: 25px;">
            <a href="/dashboard" style="color: #1a73e8; text-decoration: none; font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                ← العودة إلى لوحة التحكم
            </a>
        </div>
    </div>

    <script>
        const dropArea = document.getElementById('drop-area');
        const fileInput = document.getElementById('file-input');
        const filePreview = document.getElementById('file-preview');
        const submitBtn = document.getElementById('submit-btn');

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight() {
            dropArea.style.borderColor = '#0d47a1';
            dropArea.style.backgroundColor = '#e8f0fe';
        }

        function unhighlight() {
            dropArea.style.borderColor = '#1a73e8';
            dropArea.style.backgroundColor = '#f8f9fa';
        }

        // Handle dropped files
        dropArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            let dt = e.dataTransfer;
            let files = dt.files;
            handleFiles(files);
        }

        // Handle file selection via click
        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });

        function handleFiles(files) {
            if (files.length > 0) {
                const file = files[0];
                // Update only the preview area (keep the original file input!)
                filePreview.innerHTML = `
                    <div style="margin-bottom: 15px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#28a745" stroke-width="1.5" style="margin: 0 auto;">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                            <polyline points="22 4 12 14.01 9 11.01"></polyline>
                        </svg>
                    </div>
                    <p style="margin: 0; color: #28a745; font-weight: 600; font-size: 18px;">${file.name}</p>
                    <p style="margin: 10px 0 0; color: #5f6368; font-size: 14px;">جاهز للرفع</p>
                `;
                
                submitBtn.disabled = false;
                submitBtn.style.opacity = '1';
                submitBtn.style.cursor = 'pointer';
            }
        }
    </script>
    '''
    return render_page(content, title="رفع ملف Excel", teacher_name=teacher.username, current_page="upload")