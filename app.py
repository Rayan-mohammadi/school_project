from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import get_db_connection
import sqlite3
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# ===== دیکشنری دروس بر اساس پایه و رشته (کامل) =====
LESSONS = {
    'دهم': {
        'انسانی': [
            'فارسی (1)', 'نگارش (1)', 'دین و زندگی (1)', 
            'زبان انگلیسی (1)',
            'عربی، زبان قرآن (1)', 'آمادگی دفاعی', 
            'تفکر و سواد رسانه‌ای',
            'ریاضی و آمار (1)', 'علوم و فنون ادبی (1)', 
            'اقتصاد', 'تاریخ (1) - ایران و جهان باستان', 
            'جغرافیای ایران', 'جامعه‌شناسی (1)'
        ],
        'تجربی': [
            'فارسی (1)', 'نگارش (1)', 'دین و زندگی (1)', 
            'زبان انگلیسی (1)',
            'عربی، زبان قرآن (1)', 'آمادگی دفاعی', 
            'تفکر و سواد رسانه‌ای',
            'زیست‌شناسی (1)', 'ریاضی (1)', 'شیمی (1)', 
            'فیزیک (1)', 'آزمایشگاه علوم تجربی (1)'
        ]
    },
    'یازدهم': {
        'انسانی': [
            'فارسی (2)', 'نگارش (2)', 'دین و زندگی (2)', 
            'زبان انگلیسی (2)',
            'عربی، زبان قرآن (2)', 'تاریخ معاصر ایران', 
            'ریاضی و آمار (2)', 'علوم و فنون ادبی (2)', 
            'تاریخ (2)', 'جغرافیا (2)', 
            'جامعه‌شناسی (2)', 'فلسفه (1)', 'روان‌شناسی'
        ],
        'تجربی': [
            'فارسی (2)', 'نگارش (2)', 'دین و زندگی (2)', 
            'زبان انگلیسی (2)',
            'عربی، زبان قرآن (2)', 'تاریخ معاصر ایران', 
            'زیست‌شناسی (2)', 'ریاضی (2)', 
            'شیمی (2)', 'فیزیک (2)', 'زمین‌شناسی'
        ]
    },
    'دوازدهم': {
        'انسانی': [
            'فارسی (3)', 'نگارش (3)', 'دین و زندگی (3)', 
            'زبان انگلیسی (3)',
            'عربی، زبان قرآن (3)', 
            'ریاضی و آمار (3)', 'علوم و فنون ادبی (3)', 
            'تاریخ (3) - ایران و جهان معاصر', 
            'جغرافیا (3) (کاربردی)', 
            'جامعه‌شناسی (3)', 'فلسفه (2)'
        ],
        'تجربی': [
            'فارسی (3)', 'نگارش (3)', 'دین و زندگی (3)', 
            'زبان انگلیسی (3)',
            'عربی، زبان قرآن (3)', 
            'زیست‌شناسی (3)', 'ریاضی (3)', 
            'شیمی (3)', 'فیزیک (3)'
        ]
    }
}

# ==============================================
# ===== صفحه اصلی =====
# ==============================================
@app.route('/')
def index():
    return render_template('index.html')


# ==============================================
# ===== ثبت دانش‌آموز =====
# ==============================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    form_data = {
        'first_name': '', 'last_name': '', 'student_code': '',
        'father_name': '', 'grade': '', 'major': ''
    }
    errors = {}
    success = session.pop('success', '')

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        student_code = request.form.get('student_code', '').strip()
        father_name = request.form.get('father_name', '').strip()
        grade = request.form.get('grade', '').strip()
        major = request.form.get('major', '').strip()
        photo = request.files.get('photo')

        if not first_name: errors['first_name'] = 'وارد کردن این فیلد الزامی است'
        if not last_name: errors['last_name'] = 'وارد کردن این فیلد الزامی است'
        if not student_code: errors['student_code'] = 'وارد کردن این فیلد الزامی است'
        if not father_name: errors['father_name'] = 'وارد کردن این فیلد الزامی است'
        if not grade: errors['grade'] = 'وارد کردن این فیلد الزامی است'
        if not major: errors['major'] = 'وارد کردن این فیلد الزامی است'
        if not photo or photo.filename == '': errors['photo'] = 'وارد کردن این فیلد الزامی است'

        if not errors:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            photo_path = None
            if photo and photo.filename:
                uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
                os.makedirs(uploads_dir, exist_ok=True)
                ext = photo.filename.rsplit('.', 1)[1].lower() if '.' in photo.filename else 'jpg'
                new_filename = f"{uuid.uuid4().hex}.{ext}"
                photo_path = os.path.join('uploads', new_filename)
                photo.save(os.path.join(os.path.dirname(__file__), photo_path))
            
            try:
                cursor.execute('''
                    INSERT INTO students (first_name, last_name, student_code, father_name, grade, major, photo_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (first_name, last_name, student_code, father_name, grade, major, photo_path))
                conn.commit()
                session['success'] = 'دانش‌آموز با موفقیت ثبت شد!'
                conn.close()
                return redirect(url_for('register'))
            except sqlite3.IntegrityError:
                errors['student_code'] = 'این کد دانش‌آموزی قبلاً ثبت شده است'
                conn.close()

        form_data = {
            'first_name': first_name, 'last_name': last_name,
            'student_code': student_code, 'father_name': father_name,
            'grade': grade, 'major': major
        }

    return render_template('register.html', form_data=form_data, errors=errors, success=success)


# ==============================================
# ===== دریافت لیست دانش‌آموزان (Ajax) =====
# ==============================================
@app.route('/api/students')
def api_students():
    grade = request.args.get('grade', '')
    major = request.args.get('major', '')
    search = request.args.get('search', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM students WHERE 1=1'
    params = []
    
    if grade:
        query += ' AND grade = ?'
        params.append(grade)
    if major:
        query += ' AND major = ?'
        params.append(major)
    if search:
        query += ' AND (student_code LIKE ? OR first_name LIKE ? OR last_name LIKE ?)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param])
    
    cursor.execute(query, params)
    students = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in students])


# ==============================================
# ===== دریافت دانش‌آموزان بر اساس پایه و رشته =====
# ==============================================
@app.route('/api/students_by_grade_major')
def api_students_by_grade_major():
    grade = request.args.get('grade', '')
    major = request.args.get('major', '')
    
    if not grade or not major:
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students WHERE grade = ? AND major = ?', (grade, major))
    students = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in students])


# ==============================================
# ===== دریافت دروس بر اساس پایه و رشته =====
# ==============================================
@app.route('/api/lessons')
def api_lessons():
    grade = request.args.get('grade', '')
    major = request.args.get('major', '')
    
    if grade in LESSONS and major in LESSONS[grade]:
        return jsonify(LESSONS[grade][major])
    return jsonify([])


# ==============================================
# ===== دریافت نمرات یک دانش‌آموز برای یک درس خاص =====
# ==============================================
@app.route('/api/get_student_grade/<int:student_id>/<path:lesson>')
def get_student_grade(student_id, lesson):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT score FROM grades WHERE student_id = ? AND lesson = ?', (student_id, lesson))
    result = cursor.fetchone()
    conn.close()
    if result:
        return jsonify({'score': result['score']})
    return jsonify({'score': None})


# ==============================================
# ===== ذخیره نمرات (Ajax) =====
# ==============================================
@app.route('/api/save_grades', methods=['POST'])
def save_grades():
    data = request.get_json()
    if not data or 'grades' not in data:
        return jsonify({'status': 'error', 'message': 'داده‌ای ارسال نشده است'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for item in data['grades']:
            student_id = item['student_id']
            lesson = item['lesson']
            score = item['score']
            
            if score == '' or score is None:
                score = None
            else:
                score = float(score)
            
            cursor.execute('''
                INSERT INTO grades (student_id, lesson, score)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id, lesson) DO UPDATE SET score = ?
            ''', (student_id, lesson, score, score))
        
        conn.commit()
        return jsonify({'status': 'success', 'message': 'نمرات با موفقیت ذخیره شدند'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        conn.close()


# ==============================================
# ===== دریافت نمرات یک دانش‌آموز (همه دروس) =====
# ==============================================
@app.route('/api/get_grades/<int:student_id>')
def get_grades(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT lesson, score FROM grades WHERE student_id = ?', (student_id,))
    grades = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in grades])


# ==============================================
# ===== دریافت نمرات همه دانش‌آموزان یک کلاس =====
# ==============================================
@app.route('/api/get_all_grades')
def get_all_grades():
    grade = request.args.get('grade', '')
    major = request.args.get('major', '')
    
    if not grade or not major:
        return jsonify([])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, first_name, last_name, student_code, father_name FROM students WHERE grade = ? AND major = ?', (grade, major))
    students = cursor.fetchall()
    
    result = []
    for student in students:
        cursor.execute('SELECT lesson, score FROM grades WHERE student_id = ?', (student['id'],))
        grades = cursor.fetchall()
        grades_dict = {g['lesson']: g['score'] for g in grades}
        result.append({
            'student': dict(student),
            'grades': grades_dict
        })
    
    conn.close()
    return jsonify(result)


# ==============================================
# ===== صفحه کارنامه =====
# ==============================================
@app.route('/report')
def report():
    return render_template('report.html')


# ==============================================
# ===== صفحه ثبت نمرات =====
# ==============================================
@app.route('/grades')
def grades():
    return render_template('grades.html')


if __name__ == '__main__':
    app.run(debug=True)