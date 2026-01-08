import os
import qrcode
import io
from flask import Flask, render_template, send_file, url_for

app = Flask(__name__)
MODELS_DIR = os.path.join('static', 'models')

def get_restaurants():
    if not os.path.exists(MODELS_DIR): os.makedirs(MODELS_DIR)
    restaurants = []
    for name in os.listdir(MODELS_DIR):
        if os.path.isdir(os.path.join(MODELS_DIR, name)):
            restaurants.append({'name': name, 'logo': f"models/{name}/logo.png"})
    return restaurants

def get_menu(restaurant_name):
    path = os.path.join(MODELS_DIR, restaurant_name)
    menu = {}
    if os.path.exists(path):
        for cat in os.listdir(path):
            cat_path = os.path.join(path, cat)
            if os.path.isdir(cat_path):
                menu[cat] = []
                for f in os.listdir(cat_path):
                    if f.endswith('.glb'):
                        menu[cat].append({
                            'name': os.path.splitext(f)[0],
                            'file': f,
                            'ios': f.replace('.glb', '.usdz')
                        })
    return menu

@app.route('/')
def home(): return render_template('index.html', brands=get_restaurants())

@app.route('/menu/<restaurant>')
def view_menu(restaurant): return render_template('menu.html', restaurant=restaurant, menu=get_menu(restaurant))

@app.route('/view/<restaurant>/<category>/<item>')
def ar_view(restaurant, category, item):
    return render_template('ar_view.html', 
                           product=item, 
                           glb=url_for('static', filename=f'models/{restaurant}/{category}/{item}.glb'),
                           ios=url_for('static', filename=f'models/{restaurant}/{category}/{item}.usdz'))

@app.route('/qr/<restaurant>/<category>/<item>')
def generate_qr(restaurant, category, item):
    url = url_for('ar_view', restaurant=restaurant, category=category, item=item, _external=True)
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)