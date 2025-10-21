from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import json  # Keep this for json.dumps operations
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin

app = Flask(__name__)
app.secret_key = os.urandom(24)

def init_db():
    conn = sqlite3.connect('product_users.db')
    c = conn.cursor()

    # Create tables if they don't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            address TEXT NOT NULL,
            products_ordered TEXT NOT NULL,
            total_amount REAL NOT NULL,
            order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            image_path TEXT NOT NULL
        )
    ''')

    # Add this to your init_db() function
    c.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Insert sample products if table is empty
    product_count = c.execute('SELECT COUNT(*) FROM products').fetchone()[0]
    if product_count == 0:
        sample_products = [
            ('Band aid', 45, 'personal care', '/static/personal care/Band aid.jpeg'),
            ('Dove soap', 50, 'personal care', '/static/personal care/Dove soap.jpeg'),
            ('Dove body wash', 80, 'personal care', '/static/personal care/Dove bodywash.jpeg'),
            ('Face massager', 30, 'personal care', '/static/personal care/face massager.jpeg'),
            ('Facemask', 100, 'personal care', '/static/personal care/facemask.jpeg'),
            ('Face rollon', 100, 'personal care', '/static/personal care/face rollon.jpeg'),
            ('Foot peal mask', 100, 'personal care', '/static/personal care/Foot peal mask.jpeg'),
            ('Garnier wipes', 100, 'personal care', '/static/personal care/Garnier wipes.jpeg'),
            ('Garnier cleansing', 100, 'personal care', '/static/personal care/Garnier cleansing.jpeg'),
            ('simple facewash', 50, 'personal care', '/static/personal care/simple facewash.jpeg'),
            ('Ponds powder', 50, 'personal care', '/static/personal care/Ponds powder.jpeg'),
            ('Dove room fresh', 250, 'personal care', '/static/personal care/Dove room fresh.jpeg'),
            ('Dove spray', 150, 'personal care', '/static/personal care/Dove spray.jpeg'),
            ('Whisper', 60, 'personal care', '/static/personal care/Whisper.jpeg'),
            ('Nivea set', 200, 'personal care', '/static/personal care/Nivea set.jpeg'),
            ('Tooth.brush', 15, 'personal care', '/static/personal care/Tooth.brush.jpeg'),
            ('Colgate', 70, 'personal care', '/static/personal care/Colgate.jpeg'),
            ('Colgate toothpast', 70, 'personal care', '/static/personal care/Colgate toothpast.jpeg'),
            ('Vaseline', 30, 'personal care', '/static/personal care/Vaseline.jpeg'),
            ('Vaseline jelly', 30, 'personal care', '/static/personal care/Vaseline jelly.jpeg'),
            ('Venus razor', 30, 'personal care', '/static/personal care/Venus razor.jpeg'),
            ('Venus razor', 50, 'personal care', '/static/personal care/Venus razor.jpeg'),
            ('Ponds sunscreen', 200, 'personal care', '/static/personal care/Ponds sunscreen.jpeg'),
            ('Pantene E', 200, 'personal care', '/static/personal care/Pantene E.jpeg'),
            ('Ponds 35+', 150, 'personal care', '/static/personal care/Ponds 35+.jpeg'),
            ('Lotus', 200, 'personal care', '/static/personal care/Lotus.jpeg'),
            ('Lotus whitecream', 100, 'personal care', '/static/personal care/Lotus whitecream.jpeg'),
            ('Mac primer', 200, 'personal care', '/static/personal care/Mac primer.jpeg'),
            ('Lakme primer', 150, 'personal care', '/static/personal care/Lakme primer.jpeg'),
            ('Lakme sunscreen', 300, 'personal care', '/static/personal care/Lakme sunscreen.jpeg'),
            ('Lakme 9to5', 300, 'personal care', '/static/personal care/Lakme 9to5.jpeg'),
            ('Lavender mask', 200, 'personal care', '/static/personal care/lavender mask.jpeg'),
            ('lorial kajal', 200, 'personal care', '/static/personal care/lorial kajal.jpeg'),
            ('Castor oil', 150, 'personal care', '/static/personal care/Castor oil.jpeg'),
            ('Mac Foundation', 500, 'personal care', '/static/personal care/Mac Foundation.jpeg'),
            ('Moisturizer', 120, 'personal care', '/static/personal care/moisturizer.jpeg'),
            ('Tomato', 50, 'FruitsandVegetables', '/static/FruitsandVegetables/Tomato.jpg'),
            ('Brinjal', 50, 'FruitsandVegetables', '/static/FruitsandVegetables/Brinjal.jpeg'),
            ('Apples', 70, 'FruitsandVegetables', '/static/FruitsandVegetables/Apples.jpeg'),
            ('Capsicum', 40, 'FruitsandVegetables', '/static/FruitsandVegetables/Capsicum.jpeg'),
            ('Fenugreek', 70, 'FruitsandVegetables', '/static/FruitsandVegetables/fenugreek.jpeg'),
            ('Cauliflower', 60, 'FruitsandVegetables', '/static/FruitsandVegetables/Cauliflower.jpeg'),
            ('Cucumber', 50, 'FruitsandVegetables', '/static/FruitsandVegetables/Cocumber.jpeg'),
            ('Cabbages', 40, 'FruitsandVegetables', '/static/FruitsandVegetables/cabbages.jpeg'),
            ('Coconut', 60, 'FruitsandVegetables', '/static/FruitsandVegetables/Coconut.jpeg'),
            ('Corn', 60, 'FruitsandVegetables', '/static/FruitsandVegetables/Corn.jpeg'),
            ('Dragon fruit', 60, 'FruitsandVegetables', '/static/FruitsandVegetables/Dragon fruit.jpeg'),
            ('Ladies finger', 60, 'FruitsandVegetables', '/static/FruitsandVegetables/Ladies finger.jpeg'),
            ('Brocolli', 40, 'FruitsandVegetables', '/static/FruitsandVegetables/Coriender leafs.jpeg'),
            ('Pineapple', 60, 'FruitsandVegetables', '/static/FruitsandVegetables/Pineapple.jpeg'),
            ('Papaya', 40, 'FruitsandVegetables', '/static/FruitsandVegetables/Papaya.jpeg'),
            ('Bananas', 40, 'FruitsandVegetables', '/static/FruitsandVegetables/Bananas.jpeg'),
            ('Black grapes', 70, 'FruitsandVegetables', '/static/FruitsandVegetables/Black grapes.jpeg'),
            ('Raw mangoes', 70, 'FruitsandVegetables', '/static/FruitsandVegetables/Raw mangoes.jpeg'),
            ('Passion fruit', 70, 'FruitsandVegetables', '/static/FruitsandVegetables/Passion fruit.jpeg'),
            ('Kiwi', 100, 'FruitsandVegetables', '/static/FruitsandVegetables/Kiwi.jpeg'),
            ('Carombola', 100, 'FruitsandVegetables', '/static/FruitsandVegetables/carombola.jpeg'),
            ('Green apple', 40, 'FruitsandVegetables', '/static/FruitsandVegetables/Green apple.jpeg'),
            ('Pomegranate', 40, 'FruitsandVegetables', '/static/FruitsandVegetables/Promogranate.jpeg'),
            ('Watermelon', 40, 'FruitsandVegetables', '/static/FruitsandVegetables/Watermelon.jpeg'),
            ('Musk melon', 40, 'FruitsandVegetables', '/static/FruitsandVegetables/Musk melon.jpeg'),
            ('Butter head lettuce', 60, 'FruitsandVegetables', '/static/FruitsandVegetables/butter head lettuce.jpeg'),

            ('Amul lassi', 20, 'Dairy and breakfast', '/static/Dairy and breakfast/Amul lassi.jpeg'),
            ('Milk', 20, 'Dairy and breakfast', '/static/Dairy and breakfast/milk.jpg'),
            ('egg', 100, 'Dairy and breakfast', '/static/Dairy and breakfast/egg.jpg'),
            ('Badam drink milk', 30, 'Dairy and breakfast', '/static/Dairy and breakfast/Badam drink milk.jpeg'),
            ('Bread', 50, 'Dairy and breakfast', '/static/Dairy and breakfast/Bread.jpeg'),
            ('Brown bread', 50, 'Dairy and breakfast', '/static/Dairy and breakfast/Brown bread.jpeg'),
            ('Burger bun', 50, 'Dairy and breakfast', '/static/Dairy and breakfast/Burger bun.jpeg'),
            ('Blueberry cinnamon flax', 30, 'Dairy and breakfast', '/static/Dairy and breakfast/Blueberry cinnamon flax.jpeg'),
            ('Butter', 50, 'Dairy and breakfast', '/static/Dairy and breakfast/Butter.jpeg'),
            ('Cheese', 50, 'Dairy and breakfast', '/static/Dairy and breakfast/Cheese.jpeg'),
            ('Cheese slice', 70, 'Dairy and breakfast', '/static/Dairy and breakfast/Cheese slice.jpeg'),
            ('Coca cola tin', 40, 'Dairy and breakfast', '/static/Dairy and breakfast/Coca cola tin.jpeg'),
            ('Choco krispis', 40, 'Dairy and breakfast', '/static/Dairy and breakfast/Choco krispis.jpeg'),
            ('Coco pops', 40, 'Dairy and breakfast', '/static/Dairy and breakfast/Coco pops.jpeg'),
            ('COCONUT MILK', 40, 'Dairy and breakfast', '/static/Dairy and breakfast/COCONUT MILK.jpeg'),
            ('Cocopops chocos', 40, 'Dairy and breakfast', '/static/Dairy and breakfast/Cocopops chocos.jpeg'),
            ('Dabur honey', 40, 'Dairy and breakfast', '/static/Dairy and breakfast/Dabur honey.jpeg'),
            ('Eno', 10, 'Dairy and breakfast', '/static/Dairy and breakfast/Eno.jpeg'),
            ('Ghee', 40, 'Dairy and breakfast', '/static/Dairy and breakfast/Ghee.jpeg'),
            ('Govind lassi', 40, 'Dairy and breakfast', '/static/Dairy and breakfast/govind lassi.jpeg'),
            ('Gulab jamun', 75, 'Dairy and breakfast', '/static/Dairy and breakfast/Gulab jamun.jpeg'),
            ('Honey', 25, 'Dairy and breakfast', '/static/Dairy and breakfast/Honey.jpeg'),
            ('Jam', 25, 'Dairy and breakfast', '/static/Dairy and breakfast/Jam.jpeg'),
            ('Kissan jam', 25, 'Dairy and breakfast', '/static/Dairy and breakfast/Kissan jam.jpeg'),
            ('Red label', 50, 'Dairy and breakfast', '/static/Dairy and breakfast/tea.jpg'),
            ('Horlicks', 55, 'Dairy and breakfast', '/static/Dairy and breakfast/Horlicks.jpeg'),
            ('Mentos', 10, 'Dairy and breakfast', '/static/Dairy and breakfast/Mentos.jpeg'),
            ('Nutella', 30, 'Dairy and breakfast', '/static/Dairy and breakfast/Nutella.jpeg'),
            ('Milkmade', 55, 'Dairy and breakfast', '/static/Dairy and breakfast/Milkmade.jpeg'),
            ('Nescafe', 25, 'Dairy and breakfast', '/static/Dairy and breakfast/Nescafe.jpeg'),
            ('Nut butter', 25, 'Dairy and breakfast', '/static/Dairy and breakfast/Nut butter.jpeg'),
            ('Oatmeal', 75, 'Dairy and breakfast', '/static/Dairy and breakfast/Oatmeal.jpeg'),
            ('Sweet yogurt', 75, 'Dairy and breakfast', '/static/Dairy and breakfast/Sweet yogurt.jpeg'),
            ('Soup', 50, 'Dairy and breakfast', '/static/Dairy and breakfast/soap.jpeg'),
            ('Yippee', 50, 'Dairy and breakfast', '/static/Dairy and breakfast/yippe.jpeg'),
            ('Rava dosa', 100, 'Dairy and breakfast', '/static/Dairy and breakfast/Rava dosa.jpeg'),
            ('Quaker oat', 80, 'Dairy and breakfast', '/static/Dairy and breakfast/Quaker oat.jpeg'),
            ('Maggie', 5, 'Dairy and breakfast', '/static/Dairy and breakfast/Maggie.jpeg'),
            ('Naturalla', 30, 'Dairy and breakfast', '/static/Dairy and breakfast/Naturalla.jpeg'),
            ('Patanjali jam', 30, 'Dairy and breakfast', '/static/Dairy and breakfast/Patanjali jam.jpeg'),
            ('Mozzarellla cheese', 30, 'Dairy and breakfast', '/static/Dairy and breakfast/Mozzarellla cheese.jpeg'),
            ('Bournvita', 100, 'Dairy and breakfast', '/static/Dairy and breakfast/Bournvita.jpeg'),
            ('Peanuts smooth', 30, 'Dairy and breakfast', '/static/Dairy and breakfast/Peanuts smooth.jpeg'),
            ('Peanut butter', 70, 'Dairy and breakfast', '/static/Dairy and breakfast/Peanut butter.jpeg'),


        ('Kitkat', 20, 'Snacks and Beverages', '/static/Snacks/Kitkat.jpeg'),
        ('Kurkure', 20, 'Snacks and Beverages', '/static/Snacks/Kurkure.jpeg'),
        ('Oreo cone', 25, 'Snacks and Beverages', '/static/Snacks/Oreo cone.jpeg'),
        ('Bounty', 25, 'Snacks and Beverages', '/static/Snacks/Bounty.jpeg'),
        ('Cheetos', 30, 'Snacks and Beverages', '/static/Snacks/Cheetos.jpeg'),
        ('Chamallows', 30, 'Snacks and Beverages', '/static/Snacks/Chamallows.jpeg'),
        ('Coca cola tin', 40, 'Snacks and Beverages', '/static/Snacks/Coca cola tin.jpeg'),
        ('Cookie', 40, 'Snacks and Beverages', '/static/Snacks/Cookie.jpg'),
        ('Croissant', 30, 'Snacks and Beverages', '/static/Snacks/Croissant.jpeg'),
        ('Fanta', 50, 'Snacks and Beverages', '/static/Snacks/Fanta.jpeg'),
        ('Fanta tin', 50, 'Snacks and Beverages', '/static/Snacks/Fanta tin.jpeg'),
        ('Hersheys', 40, 'Snacks and Beverages', '/static/Snacks/Hersheys.jpeg'),
        ('kinder joy', 50, 'Snacks and Beverages', '/static/Snacks/kinder joy.jpeg'),
        ('Kitkat cone', 50, 'Snacks and Beverages', '/static/Snacks/Kitkat cone.jpeg'),
        ('Lassi', 30, 'Snacks and Beverages', '/static/Snacks/Lassi.jpeg'),
        ('Lays combo', 70, 'Snacks and Beverages', '/static/Snacks/Lays combo.jpeg'),
        ('Lays salt', 20, 'Snacks and Beverages', '/static/Snacks/Lays salt.jpeg'),
        ('Lychee lassi', 20, 'Snacks and Beverages', '/static/Snacks/Lychee lassi.jpeg'),
        ('Madangles', 25, 'Snacks and Beverages', '/static/Snacks/Madangles.jpeg'),
        ('MARIEGOLD', 25, 'Snacks and Beverages', '/static/Snacks/MARIEGOLD.jpeg'),
        ('Mentos', 10, 'Snacks and Beverages', '/static/Snacks/Mentos.jpeg'),
        ('Nutella', 30, 'Snacks and Beverages', '/static/Snacks/Nutella.jpeg'),
        ('Oreo bites', 15, 'Snacks and Beverages', '/static/Snacks/Oreo bites.jpeg'),
        ('Oreo icecream', 60, 'Snacks and Beverages', '/static/Snacks/Oreo icecream.jpeg'),
        ('PARLEG', 10, 'Snacks and Beverages', '/static/Snacks/PARLEG.jpeg'),
        ('Pepsi', 25, 'Snacks and Beverages', '/static/Snacks/Pepsi.jpeg'),
        ('Pepsi tin', 25, 'Snacks and Beverages', '/static/Snacks/Pepsi tin.jpeg'),
        ('Sprite', 25, 'Snacks and Beverages', '/static/Snacks/Sprite.jpeg'),
        ('Sprite lemon', 25, 'Snacks and Beverages', '/static/Snacks/Sprite lemon.jpeg'),
        ('Sting', 25, 'Snacks and Beverages', '/static/Snacks/Sting.jpeg'),
        ('Peanuts', 100, 'Snacks and Beverages', '/static/Snacks/Peanuts.jpeg'),
        ('M and M', 20, 'Snacks and Beverages', '/static/Snacks/M nd M.jpeg'),
        ('Duplo chocnut', 20, 'Snacks and Beverages', '/static/Snacks/Duplo chocnut.jpeg'),


            ('Dove kit',        150, 'Baby Care', '/static/Baby Care/Dove kit.jpeg'),
            ('Huggies',         200, 'Baby Care', '/static/Baby Care/Huggies.jpeg'),
            ('Huggies wipes',   175, 'Baby Care', '/static/Baby Care/Huggies wipes.jpeg'),
            ('Johnsons kit',    300, 'Baby Care', '/static/Baby Care/Johnsons kit.jpeg'),
            ('Johnsons powder', 250, 'Baby Care', '/static/Baby Care/Johnsons powder.jpeg'),
            ('Johnsons Shampoo',200, 'Baby Care', '/static/Baby Care/Johnsons Shampoo.jpeg'),
            ('Johnsons shampoos',400,'Baby Care', '/static/Baby Care/Johnsons shampoos.jpeg'),
            ('Mamy poko pants', 200, 'Baby Care', '/static/Baby Care/Mamy poko pants.jpeg'),
            ('Mamy poko pants l',200, 'Baby Care', '/static/Baby Care/Mamy poko pants l.jpeg'),
            ('Mamy poko pants s4',200,'Baby Care', '/static/Baby Care/Mamy poko pants s4.jpeg'),
            ('Pampers',         200, 'Baby Care', '/static/Baby Care/Pampers.jpeg'),
            ('Pampers wipes',   200, 'Baby Care', '/static/Baby Care/Pampers wipes.jpeg'),
            ('Baby biscuits',    75, 'Baby Care', '/static/Baby Care/Baby biscuits.jpeg'),
            ('Nestle cereales', 300, 'Baby Care', '/static/Baby Care/Nestle cereales.jpeg'),

            ('Jeera powder', 250, 'Grocery', '/static/Grocery/Jeera powder.jpeg'),
            ('Kasuri methi', 250, 'Grocery', '/static/Grocery/Kasuri methi.jpeg'),
            ('Green moong', 250, 'Grocery', '/static/Grocery/Green moong.jpeg'),
            ('Clove', 70, 'Grocery', '/static/Grocery/Clove.jpeg'),
            ('Chakki atta', 300, 'Grocery', '/static/Grocery/Chakki atta.jpeg'),
            ('Ragi flour', 300, 'Grocery', '/static/Grocery/Ragi flour.jpeg'),
            ('Jasmine rice', 300, 'Grocery', '/static/Grocery/Jasmine rice.jpeg'),
            ('Basmathi rice', 300, 'Grocery', '/static/Grocery/Basmathi rice.jpeg'),
            ('Masala vadamix', 250, 'Grocery', '/static/Grocery/Masala vadamix.jpeg'),
            ('Black seeds', 70, 'Grocery', '/static/Grocery/Black seeds.jpeg'),
            ('Mutton masala', 50, 'Grocery', '/static/Grocery/Mutton masala.jpeg'),
            ('Sugar', 150, 'Grocery', '/static/Grocery/Sugar.jpeg'),
            ('Salt', 150, 'Grocery', '/static/Grocery/Salt.jpeg'),
            ('Aashirvad salt', 150, 'Grocery', '/static/Grocery/Aashirvad salt.jpeg'),
            ('Kasoori methi', 150, 'Grocery', '/static/Grocery/Kasoori methi.jpeg'),
            ('Green cardomom', 250, 'Grocery', '/static/Grocery/Green cardomom.jpeg'),
            ('Cardomom', 250, 'Grocery', '/static/Grocery/Cardomom.jpeg'),
            ('Cardomom pods', 250, 'Grocery', '/static/Grocery/Cardomom pods.jpeg'),
            ('Coriander powder', 250, 'Grocery', '/static/Grocery/Coriander powder.jpeg'),
            ('Besan', 150, 'Grocery', '/static/Grocery/Besan.jpeg'),
            ('Masoor dal', 150, 'Grocery', '/static/Grocery/Masoor dal.jpeg'),
            ('Organic kalonji', 300, 'Grocery', '/static/Grocery/Organic kalonji.jpeg'),
            ('Cumin ground 180g', 300, 'Grocery', '/static/Grocery/Cumin ground 180g.jpeg'),
            ('Moong dal', 300, 'Grocery', '/static/Grocery/Moong dal.jpeg'),
            ('Cardomom seeds', 170, 'Grocery', '/static/Grocery/Cardomom seeds.jpeg'),
            ('Cardomom seeds 50g', 80, 'Grocery', '/static/Grocery/Cardomom seeds 50g.jpeg'),
            ('Atta', 280, 'Grocery', '/static/Grocery/Atta.jpeg'),
            ('Ground cumin', 150, 'Grocery', '/static/Grocery/Ground cumin.jpeg'),
            ('Biryani masala', 150, 'Grocery', '/static/Grocery/Biryani masala.jpeg'),
            ('Sticky rice', 350, 'Grocery', '/static/Grocery/Sticky rice.jpeg'),
            ('Sweet rice', 200, 'Grocery', '/static/Grocery/Sweet rice.jpeg'),
            ('Toor dal', 200, 'Grocery', '/static/Grocery/Toor dal.jpeg'),
            ('Tata chanadal', 200, 'Grocery', '/static/Grocery/Tata chanadal.jpeg'),
            ('Fish curry masala', 200, 'Grocery', '/static/Grocery/Fish curry masala.jpeg'),
            ('Dal tadka', 200, 'Grocery', '/static/Grocery/Dal tadka.jpeg'),
            ('Garam masala', 60, 'Grocery', '/static/Grocery/Garam masala.jpeg'),
            ('organic moong dal', 100, 'Grocery', '/static/Grocery/organic moong dal.jpeg'),
            ('Pickle', 100, 'Grocery', '/static/Grocery/Pickle.jpeg'),
            ('Pizza sause', 100, 'Grocery', '/static/Grocery/Pizza sause.jpeg'),
            ('Rice', 300, 'Grocery', '/static/Grocery/Rice.jpeg'),
            ('Natco rice flour', 300, 'Grocery', '/static/Grocery/Natco rice flour.jpeg'),
            ('Urad dal', 100, 'Grocery', '/static/Grocery/Urad dal.jpeg'),
            ('Multigrain atta', 400, 'Grocery', '/static/Grocery/Multigrain atta.jpeg'),


            ('Aer', 120, 'House Hold', '/static/household/Aer.jpeg'),
            ('Air fresher', 120, 'House Hold', '/static/household/Air fresher.jpeg'),
            ('Air mist', 100, 'House Hold', '/static/household/Air mist.jpeg'),
            ('Air wick', 100, 'House Hold', '/static/household/Air wick.jpeg'),
            ('aireal', 200, 'House Hold', '/static/household/aireal.jpeg'),
            ('Attack', 200, 'House Hold', '/static/household/Attack.jpeg'),
            ('Clip', 60, 'House Hold', '/static/household/Clip.jpeg'),
            ('clorox', 60, 'House Hold', '/static/household/clorox.jpeg'),
            ('dettol', 50, 'House Hold', '/static/household/dettol.jpeg'),
            ('dishwasher', 100, 'House Hold', '/static/household/dishwasher.jpeg'),
            ('downy', 100, 'House Hold', '/static/household/downy.jpeg'),
            ('Downy cleaner', 100, 'House Hold', '/static/household/Downy cleaner.jpeg'),
            ('dust pan', 80, 'House Hold', '/static/household/dust pan.jpeg'),
            ('dustbin', 80, 'House Hold', '/static/household/dustbin.jpeg'),
            ('dustbin cover', 80, 'House Hold', '/static/household/dustbin cover.jpeg'),
            ('Febreze', 80, 'House Hold', '/static/household/Febreze.jpeg'),
            ('Fairy', 90, 'House Hold', '/static/household/Fairy.jpeg'),
            ('Glade', 100, 'House Hold', '/static/household/Glade.jpeg'),
            ('Glade spray', 100, 'House Hold', '/static/household/Glade spray.jpeg'),
            ('Glade air', 100, 'House Hold', '/static/household/Glade air.jpeg'),
            ('Glat set', 100, 'House Hold', '/static/household/Glat set.jpeg'),
            ('Harpic', 300, 'House Hold', '/static/household/Harpic.jpeg'),
            ('Lenor', 150, 'House Hold', '/static/household/Lenor.jpeg'),
            ('mop', 150, 'House Hold', '/static/household/mop.jpeg'),
            ('Pril', 150, 'House Hold', '/static/household/Pril.jpeg'),
            ('Room spray', 230, 'House Hold', '/static/household/Room spray.jpeg'),
            ('Softouch', 250, 'House Hold', '/static/household/Softouch.jpeg'),
            ('sponge', 400, 'House Hold', '/static/household/sponge.jpeg'),
            ('spray bottles', 400, 'House Hold', '/static/household/spray bottles.jpeg'),
            ('Tide', 240, 'House Hold', '/static/household/tide.jpeg'),
            ('Tub', 270, 'House Hold', '/static/household/tub.jpeg'),
            ('Vanish', 300, 'House Hold', '/static/household/Vanish.jpeg'),

            ('Apron', 275, 'Home and Kitchen', '/static/kitchen/Apron.jpeg'),
            ('Boul set', 320, 'Home and Kitchen', '/static/kitchen/Boul set.jpeg'),
            ('Chopper', 250, 'Home and Kitchen', '/static/kitchen/Chopper.jpeg'),
            ('Container', 200, 'Home and Kitchen', '/static/kitchen/Container.jpeg'),
            ('Crocy holder', 200, 'Home and Kitchen', '/static/kitchen/Crocy holder.jpeg'),
            ('Cutter', 200, 'Home and Kitchen', '/static/kitchen/Cutter.jpeg'),
            ('Cutting board', 200, 'Home and Kitchen', '/static/kitchen/Cutting board.jpeg'),
            ('Glass set', 150, 'Home and Kitchen', '/static/kitchen/Glass set.jpeg'),
            ('Grain container', 150, 'Home and Kitchen', '/static/kitchen/Grain container.jpeg'),
            ('Jar', 150, 'Home and Kitchen', '/static/kitchen/Jar.jpeg'),
            ('Knife holder', 150, 'Home and Kitchen', '/static/kitchen/Knife holder.jpeg'),
            ('Plate set', 400, 'Home and Kitchen', '/static/kitchen/Plate set.jpeg'),
            ('Round pan', 400, 'Home and Kitchen', '/static/kitchen/Round pan.jpeg'),
            ('Spice holder', 400, 'Home and Kitchen', '/static/kitchen/Spice holder.jpeg')
        ]

        c.executemany('''
            INSERT INTO products (name, price, category, image_path)
            VALUES (?, ?, ?, ?)
        ''', sample_products)

    conn.commit()
    conn.close()


init_db()


def get_db_connection():
    conn = sqlite3.connect('product_users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def intro():
    return render_template('intro.html')

@app.route('/index')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products LIMIT 6').fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # Store plain text password

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                         (name, email, password))  # Store plain text
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
        finally:
            conn.close()
    return render_template('signup.html')

def is_safe_url(target):
    """Check if URL is safe for redirects to prevent open redirect vulnerabilities."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    # Get next URL from request parameters
    next_url = request.args.get('next')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        next_url = request.form.get('next')  # Get next URL from form

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            flash('Login successful!', 'success')

            # Safe redirect handling
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for('index'))  # Changed from 'index'

        flash('Invalid email or password', 'error')

    return render_template('login.html', next_url=next_url)


# Add this new route for contact us


@app.route('/contact_us', methods=['GET', 'POST'])
def contact_us():
    if 'user_id' not in session:
        return redirect(url_for('login', next=url_for('contact_us')))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()

    if not user:
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('logout'))

    name = user['name']
    email = user['email']

    phone = ''
    subject = ''
    message = ''

    if request.method == 'POST':
        phone = request.form.get('phone', '')
        subject = request.form.get('subject', '')
        message = request.form.get('message', '')

        if not subject or not message:
            flash('Subject and message are required!', 'error')
            return render_template('contact_us.html',
                                   name=name,
                                   email=email,
                                   phone=phone,
                                   subject=subject,
                                   message=message)

        # Add 5 hours 30 minutes to UTC time to get IST
        ist_time = datetime.utcnow() + timedelta(hours=5, minutes=30)

        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO contact_messages (user_id, name, email, phone, subject, message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session['user_id'], name, email, phone, subject, message, ist_time.strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('contact_us'))
        except Exception as e:
            flash(f'Error sending message: {str(e)}', 'error')
        finally:
            conn.close()

    return render_template('contact_us.html',
                           name=name,
                           email=email,
                           phone=phone,
                           subject=subject,
                           message=message)

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data received'}), 400

        # Validate required fields
        required_fields = ['full_name', 'phone_number', 'address', 'products', 'total_amount']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400

        # Use products directly from request (already contain image_path)
        products_json = json.dumps(data['products'])

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO orders (user_id, full_name, phone_number, address, products_ordered, total_amount)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            data['full_name'],
            data['phone_number'],
            data['address'],
            products_json,
            data['total_amount']
        ))
        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        app.logger.error(f'Order error: {str(e)}')
        return jsonify({'success': False, 'message': 'Server error'}), 500


# Update the cart page to redirect to payment after login
@app.route('/cart')
def cart():
    # If user is logged in, show cart normally
    if 'user_id' in session:
        return render_template('cart.html')

    # If not logged in, redirect to login with payment as next destination
    return redirect(url_for('login', next=url_for('payment')))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')




@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders WHERE user_id = ?', (session['user_id'],)).fetchall()

    parsed_orders = []
    for order in orders:
        order_dict = dict(order)
        order_dict['products'] = json.loads(order_dict['products_ordered'])

        # Convert string to datetime object
        order_date = datetime.strptime(order_dict['order_date'], '%Y-%m-%d %H:%M:%S')
        order_dict['order_date'] = order_date  # Replace string with datetime object

        parsed_orders.append(order_dict)

    conn.close()
    return render_template('orders.html', orders=parsed_orders)

@app.route('/vegetables')
def vegetables():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products WHERE category = ?', ('vegetables',)).fetchall()
    conn.close()
    return render_template('Vegetables.html', products=products)


@app.route('/grocery')
def grocery():
    return render_template('Grocery.html')


@app.route('/home_kitchen')
def home_kitchen():
    return render_template('home_kitchen.html')


@app.route('/baby_care')
def baby_care():
    return render_template('baby_care.html')


@app.route('/household_items')
def household_items():
    return render_template('household_items.html')


@app.route('/personal_care')
def personal_care():
    return render_template('personal_care.html')

@app.route('/onion')
def onion():
    return render_template('Fruits and Vegetables/onion.html')

@app.route('/tomato')
def tomato():
    return render_template('Fruits and Vegetables/tomato.html')


@app.route('/snacks_beverages')
def snacks_beverages():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products WHERE category = ?', ('snacks',)).fetchall()
    conn.close()
    return render_template('snacks_beverages.html', products=products)


@app.route('/dairy_breakfast')
def dairy_breakfast():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products WHERE category = ?', ('dairy',)).fetchall()
    conn.close()
    return render_template('dairy_breakfast.html', products=products)
# Update the payment route to pass next parameter
@app.route('/payment')
def payment():
    if 'user_id' not in session:
        # Pass payment URL as next parameter
        return redirect(url_for('login', next=request.url))
    return render_template('payment.html')

@app.route('/privacy_policy_signup')
def privacy_policy_signup():
    return render_template('privacy_policy_signup.html')


@app.route('/privacy_policy_login')
def privacy_policy_login():
    return render_template('privacy_policy_login.html')


@app.route('/privacy_policy_signup_home')
def privacy_policy_signup_home():
    return render_template('privacy_policy_signup_home.html')


@app.route('/terms_login')
def terms_login():
    return render_template('terms_login.html')


@app.route('/terms_signup')
def terms_signup():
    return render_template('terms_signup.html')


@app.route('/terms_signup_home')
def terms_signup_home():
    return render_template('terms_signup_home.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')



@app.route('/logout')
def logout():
    session.clear()
    # Clear client-side flag
    return redirect(url_for('intro'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
