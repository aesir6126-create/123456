import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# 嘗試載入本機的 .env 檔案（雲端環境沒有也不會報錯）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 檢查是否有設定 DATABASE_URL，若沒有則直接終止程式
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("錯誤：尚未設定 DATABASE_URL 環境變數！請先設定後再執行程式。")

app = Flask(__name__)

# 資料庫連線設定
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==================== 資料庫模型定義 ====================
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

# ==================== 路由與視圖函式 ====================
@app.route('/')
def index():
    try:
        # 取得所有 50嵐 與 Macu 的品項供點餐使用
        items_50lan = MenuItem.query.filter_by(brand='50嵐').all()
        items_macu = MenuItem.query.filter_by(brand='Macu').all()
    except Exception as e:
        items_50lan = []
        items_macu = []
        print(f"資料庫查詢錯誤: {e}")
    
    return render_template('index.html', items_50lan=items_50lan, items_macu=items_macu)

@app.route('/add_order', methods=['POST'])
def add_order():
    brand = request.form.get('brand')
    item_name = request.form.get('item_name')
    qty = request.form.get('qty', type=int)

    if brand and item_name and qty:
        try:
            new_order = OrderRecord(brand=brand, item_name=item_name, qty=qty)
            db.session.add(new_order)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"新增訂單錯誤: {e}")

    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        # 自動建立資料庫表格（若尚未建立）
        db.create_all()
    
    # 支援 Render 動態指派的 Port，若本地執行則預設為 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
