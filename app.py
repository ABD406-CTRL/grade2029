from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__) # تصحيح بسيط لـ name

EXCEL_FILE = '2029دفعة.xlsx'

def get_student_data(query):
    try:
        # قراءة الملف
        df = pd.read_excel(EXCEL_FILE, header=None)
        
        # تحويل الاستعلام لنص عشان نقارنه بالأسماء
        query_str = str(query).strip()
        
        # هلق بنحدد الأعمدة اللي بدنا نبحث فيها:
        # العمود 0: الرقم الجامعي | العمود 3: الرقم الامتحاني | العمود 5: الاسم الكامل
        # بنستخدم .astype(str) عشان نضمن إن المقارنة نصية وما يضرب الكود
        mask = (df[0].astype(str) == query_str) | \
               (df[1].astype(str) == query_str) | \
               (df[5].astype(str) == query_str)  | \
                              (df[4].astype(str) == query_str)


        
        student_row = df[mask]
        
        if not student_row.empty:
            # تحويل السطر لقائمة (List)
            return student_row.iloc[0].tolist()
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('student_id')
    # ما عاد في داعي نحول لـ int هون لأننا عم نقارن نصوص (str) بالكود فوق، وهاد أضمن
    
    student = get_student_data(query)
    if student:
        return render_template('student.html', s=student)
    return "<h3>الطالب غير موجود</h3><a href='/'>رجوع</a>"
@app.route('/sort', methods=['POST'])
def sort_students():
    try:
        # 1. استلام رقم العمود الذي اختاره المستخدم من القائمة المنسدلة
        col_index = int(request.form.get('column_index'))
        
        # 2. قراءة بيانات ملف الإكسل
        df = pd.read_excel(EXCEL_FILE, header=None)
        
        # 3. تحويل بيانات العمود المختار لأرقام (عشان الترتيب يكون صحيح 100، 99، 98...)
        # وإذا كان هناك نص (مثل كلمة "غائب") سيحولها لـ NaN لكي لا ينهار الكود
        df[col_index] = pd.to_numeric(df[col_index], errors='coerce')
        
        # 4. ترتيب البيانات تنازلياً (من الأعلى للأدنى) وحذف الفراغات في هذا العمود
        df_sorted = df.dropna(subset=[col_index]).sort_values(by=col_index, ascending=False)
        
        # 5. تحويل النتيجة لقائمة وإرسالها لـ index.html لعرض الجدول
        results = df_sorted.values.tolist()
        return render_template('index.html', results=results, sorted_col=col_index)
    except Exception as e:
        return f"حدث خطأ أثناء الفرز: {e}"

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)