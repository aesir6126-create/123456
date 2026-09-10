from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'fifty_lan_secret_key'

menu_data = [
    {"id": 1, "category": "找奶茶", "name": "奶綠", "M": 40, "L": 55},
    {"id": 2, "category": "找奶茶", "name": "奶茶", "M": 40, "L": 55},
    {"id": 3, "category": "找奶茶", "name": "烏龍奶", "M": 40, "L": 55},
    {"id": 4, "category": "找奶茶", "name": "阿華田", "M": 45, "L": 60},
    {"id": 5, "category": "找奶茶", "name": "可可芭蕾", "M": 50, "L": 65},
    {"id": 6, "category": "找奶茶", "name": "波霸奶茶", "M": 40, "L": 55},
    {"id": 7, "category": "找奶茶", "name": "珍珠奶茶", "M": 40, "L": 55},
    {"id": 8, "category": "找好茶", "name": "黃金烏龍", "M": 30, "L": 35},
    {"id": 9, "category": "找好茶", "name": "四季春青茶", "M": 30, "L": 35},
    {"id": 10, "category": "找好茶", "name": "微檸檬紅/青", "M": 35, "L": 45},
]

ICE_OPTIONS = ["正常冰", "少冰", "微冰", "去冰", "完全去冰"]
SUGAR_OPTIONS = ["正常糖", "少糖", "半糖", "微糖", "無糖"]

@app.route('/')
def index():
    if 'cart' not in session:
        session['cart'] = []
    
    cart = session['cart']
    total_amount = sum(item['total'] for item in cart)
    
    return render_template('index.html', 
                           menu=menu_data, 
                           ice_options=ICE_OPTIONS, 
                           sugar_options=SUGAR_OPTIONS, 
                           cart=cart, 
                           total_amount=total_amount)

@app.route('/add', methods=['POST'])
def add_to_cart():
    item_id = int(request.form.get('item_id'))
    size = request.form.get('size')
    sugar = request.form.get('sugar')
    ice = request.form.get('ice')
    qty = int(request.form.get('qty', 1))
    
    selected_item = next((item for item in menu_data if item['id'] == item_id), None)
    
    if selected_item:
        price = selected_item['M'] if size == 'M' else selected_item['L']
        size_text = "中杯(M)" if size == 'M' else "大杯(L)"
        total_price = price * qty
        
        cart_item = {
            "name": selected_item['name'],
            "size": size_text,
            "sugar": sugar,
            "ice": ice,
            "price": price,
            "qty": qty,
            "total": total_price
        }
        
        if 'cart' not in session:
            session['cart'] = []
            
        session['cart'].append(cart_item)
        session.modified = True
        
    return redirect(url_for('index'))

@app.route('/clear')
def clear_cart():
    session['cart'] = []
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)