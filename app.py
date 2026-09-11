import os
from flask import Flask, render_template, request, redirect, url_for
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

# 自動初始化測試菜單資料
with app.app_context():
    db.create_all()
    if MenuItem.query.count() == 0:
        sample_items = [
            MenuItem(brand="50嵐", name="茉莉綠茶"),
            MenuItem(brand="50嵐", name="四季春青茶"),
            MenuItem(brand="50嵐", name="波霸奶茶"),
            MenuItem(brand="大苑子", name="愛文芒果冰沙"),
            MenuItem(brand="大苑子", name="柳橙綠茶"),
            MenuItem(brand="麻古茶坊", name="芝芝葡萄果粒"),
            MenuItem(brand="麻古茶坊", name="楊枝甘露")
        ]
        db.session.bulk_save_objects(sample_items)
        db.session.commit()

# 前台：點餐頁面
@app.route('/')
def index():
    try:
        menu_items = MenuItem.query.all()
        brands = sorted(list(set(item.brand for item in menu_items)))
        all_orders = OrderRecord.query.all()
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
    
    selected_item = MenuItem.query.get(item_id)
    
    if selected_item:
        new_order = OrderRecord(
            brand=selected_item.brand,
            item_name=selected_item.name,
            qty=qty,
            sweetness=sweetness,
            ice=ice
        )
        db.session.add(new_order)
        db.session.commit()
        
    return redirect(url_for('index'))

# 前台：清除訂單紀錄
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
