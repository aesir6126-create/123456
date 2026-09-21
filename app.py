import os
import csv
import io
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'general_order_secret_key'

# Supabase 連線設定
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres.caeoewoadclblbnjwjgg:gc001284614564@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)

class OrderRecord(db.Model):
    __tablename__ = 'order_record'
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    sweetness = db.Column(db.String(20), nullable=False)
    ice = db.Column(db.String(20), nullable=False)
    note = db.Column(db.String(200), nullable=True)  # 新增：備註欄位
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 自動初始化測試菜單資料
with app.app_context():
    db.create_all()
    # 如果資料庫沒有 note 欄位，在第一次執行時 SQLAlchemy 建立表格會自動帶入，若舊表格已存在建議到 Supabase 檢查或手動新增 note 欄位 (TEXT)

# 前台：點餐頁面
@app.route('/')
def index():
    try:
        menu_items = MenuItem.query.all()
        brands = sorted(list(set(item.brand for item in menu_items)))
        all_orders = OrderRecord.query.order_by(OrderRecord.created_at.desc()).all()
        
        # 將資料庫的 UTC 時間轉換為台灣時間 (UTC+8)
        for order in all_orders:
            if order.created_at:
                order.created_at = order.created_at + timedelta(hours=8)
                
    except Exception as e:
        print(f"資料庫查詢錯誤: {e}")
        menu_items = []
        brands = []
        all_orders = []
    
    return render_template('index.html', menu_items=menu_items, brands=brands, orders=all_orders)

# 前台：加入訂單
@app.route('/add', methods=['POST'])
def add_to_cart():
    item_id = request.form.get('item_id')
    qty = int(request.form.get('qty', 1))
    sweetness = request.form.get('sweetness', '正常甜')
    ice = request.form.get('ice', '正常冰')
    note = request.form.get('note', '').strip()  # 接收備註內容
    
    selected_item = MenuItem.query.get(item_id)
    
    if selected_item:
        new_order = OrderRecord(
            brand=selected_item.brand,
            item_name=selected_item.name,
            qty=qty,
            sweetness=sweetness,
            ice=ice,
            note=note  # 存入資料庫
        )
        db.session.add(new_order)
        db.session.commit()
        
    return redirect(url_for('index'))

# 前台：單筆刪除訂單
@app.route('/delete/<int:id>', methods=['POST'])
def delete_order(id):
    order = OrderRecord.query.get_or_404(id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('index'))

# 前台：清除全部訂單紀錄
@app.route('/clear', methods=['POST'])
def clear_history():
    OrderRecord.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

# 後台：管理選單主頁
@app.route('/admin')
def admin_menu():
    items = MenuItem.query.all()
    edit_item = None
    edit_id = request.args.get('edit_id')
    if edit_id:
        edit_item = MenuItem.query.get(edit_id)
    return render_template('admin.html', items=items, edit_item=edit_item)

# 後台：新增品項
@app.route('/admin/add', methods=['POST'])
def admin_add():
    brand = request.form.get('brand')
    name = request.form.get('name')
    if brand and name:
        new_item = MenuItem(brand=brand, name=name)
        db.session.add(new_item)
        db.session.commit()
    return redirect(url_for('admin_menu'))

# 後台：更新品項
@app.route('/admin/update/<int:id>', methods=['POST'])
def admin_update(id):
    item = MenuItem.query.get_or_404(id)
    item.brand = request.form.get('brand')
    item.name = request.form.get('name')
    db.session.commit()
    return redirect(url_for('admin_menu'))

# 後台：刪除品項
@app.route('/admin/delete/<int:id>', methods=['POST'])
def admin_delete(id):
    item = MenuItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_menu'))

# 後台：匯出 CSV 檔 (Big5 編碼)
@app.route('/admin/export')
def admin_export_csv():
    items = MenuItem.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['brand', 'name'])
    for item in items:
        writer.writerow([item.brand, item.name])
    output.seek(0)
    csv_data = output.getvalue().encode('big5', errors='ignore')
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=menu_items.csv"}
    )

# 後台：匯入 CSV 檔 (自動偵測編碼)
@app.route('/admin/import', methods=['POST'])
def admin_import_csv():
    if 'csv_file' not in request.files:
        return redirect(url_for('admin_menu'))
    file = request.files['csv_file']
    if file.filename == '':
        return redirect(url_for('admin_menu'))
    if file:
        try:
            file_bytes = file.read()
            decoded_text = None
            for enc in ['utf-8-sig', 'big5', 'cp950', 'utf-8']:
                try:
                    decoded_text = file_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if decoded_text:
                stream = io.StringIO(decoded_text)
                reader = csv.reader(stream)
                header = next(reader, None)
                if header:
                    for row in reader:
                        if len(row) >= 2:
                            brand = row[0].strip()
                            name = row[1].strip()
                            if brand and name:
                                existing = MenuItem.query.filter_by(brand=brand, name=name).first()
                                if not existing:
                                    new_item = MenuItem(brand=brand, name=name)
                                    db.session.add(new_item)
                    db.session.commit()
        except Exception as e:
            print(f"CSV 匯入錯誤: {e}")
    return redirect(url_for('admin_menu'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
