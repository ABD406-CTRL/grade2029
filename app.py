from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os

app = Flask(__name__)

EXCEL_FILE = '2029دفعة.xlsx'

def load_data():
    # قراءة الملف (تأكد أن الأعمدة مرتبة كما في الكود)
    return pd.read_excel(EXCEL_FILE, header=None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sort', methods=['POST'])
def sort_students():
    try:
        col_index = int(request.form.get('column_index'))
        df = load_data()
        
        # تحويل العمود لأرقام للفرز الصحيح
        df[col_index] = pd.to_numeric(df[col_index], errors='coerce')
        
        # فرز تنازلي (الأعلى أولاً)
        df_sorted = df.dropna(subset=[col_index]).sort_values(by=col_index, ascending=False)
        
        # إضافة الترتيب (1, 2, 3...)
        df_sorted['rank'] = range(1, len(df_sorted) + 1)
        
        results = df_sorted.values.tolist()
        # نرسل اسم العمود المختار للعرض
        col_name = request.form.get('column_name', 'الدرجة')
        
        return render_template('index.html', results=results, sorted_col=col_index, col_name=col_name)
    except Exception as e:
        return f"حدث خطأ: {e}"

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('student_id')
    df = load_data()
    mask = (df[0].astype(str) == str(query)) | (df[5].astype(str) == str(query))
    student_row = df[mask]
    if not student_row.empty:
        return render_template('student.html', s=student_row.iloc[0].tolist())
    return "<h3>الطالب غير موجود</h3><a href='/'>رجوع</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)