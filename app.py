import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
    
app = Flask(__name__)
app.secret_key = 'fifty_lan_secret_key'

# 自動讀取環境變數中的 DATABASE_URL (Supabase)
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# 如果沒有設定 DATABASE_URL，就退回使用本機的 SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 1. 商品選單 Model（對應 supabase 的 menu_items 表格）
class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)

# 2. 點餐紀錄 Model（對應 supabase 的 order_record 表格）
class OrderRecord(db.Model):
    __tablename__ = 'order_record'
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

# 建立表格（若雲端已經手動建好，這行會自動對應）
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    # 從 Supabase 撈出所有菜單與歷史訂單
    menu_data = MenuItem.query.all()
    all_orders = OrderRecord.query.all()
    
    return render_template('index.html', 
                           menu=menu_data, 
                           orders=all_orders)

@app.route('/add', methods=['POST'])
def add_to_cart():
    item_id = request.form.get('item_id')
    qty = int(request.form.get('qty', 1))
    
    # 從資料庫找出對應的商品
    selected_item = MenuItem.query.get(item_id)
    
    if selected_item:
        new_order = OrderRecord(
            brand=selected_item.brand,
            item_name=selected_item.name,
            qty=qty
        )
        db.session.add(new_order)
        db.session.commit()
        
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_history():
    OrderRecord.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
