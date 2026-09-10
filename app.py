import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'general_order_secret_key'

database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///orders.db'
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

@app.route('/')
def index():
    try:
        # 直接抓取所有品項，不特別分類品牌
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
