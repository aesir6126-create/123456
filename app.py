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
            MenuItem(brand="精選茶飲", name="茉莉綠茶 / 阿薩姆紅茶"),
            MenuItem(brand="精選茶飲", name="四季春青茶"),
            MenuItem(brand="精選茶飲", name="黃金烏龍"),
            MenuItem(brand="精選茶飲", name="椰果紅 / 綠"),
            MenuItem(brand="精選茶飲", name="波霸紅 / 綠")
        ]
        db.session.bulk_save_objects(sample_items)
        db.session.commit()

@app.route('/')
def index():
    try:
        menu_data = MenuItem.query.all()
        all_orders = OrderRecord.query.all()
    except Exception as e:
        print(f"資料庫查詢錯誤: {e}")
        menu_data = []
        all_orders = []
    
    return render_template('index.html', menu=menu_data, orders=all_orders)

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

@app.route('/clear', methods=['POST'])
def clear_history():
    OrderRecord.query.delete()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
