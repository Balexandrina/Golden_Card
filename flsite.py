import sqlite3
import os
from flask import Flask, render_template, request, g, flash, abort
from FDataBase import FDataBase

DATABASE = 'flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db')))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn 

def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html', menu = dbase.getMenu())

@app.route('/about')
def about():
    return render_template('about.html', title='О нас')

@app.route('/catalog')
def catalog():
    return render_template('product_catalog.html', title='Каталог продукции')

@app.route("/add_feedback", methods=["POST", "GET"])
def addReview():
    db = get_db()
    dbase = FDataBase(db)
 
    if request.method == "POST":
        if len(request.form['name']) > 2 and len(request.form['post']) > 2: # basic
            res = dbase.addReview(request.form['name'], request.form['post']) 
            if not res:
                flash('Ошибка добавления отзыва', category = 'error')
            else:
                flash('Благодарим за отзыв!', category='success')
        else:
            flash('Ошибка добавления отзыва', category='error')
 
    return render_template('add_feedback.html', menu = dbase.getMenu(), title="Отзывы", posts = dbase.getPostsAnonce()) 

@app.route("/post/<alias>")
def showPost(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)

if __name__ == '__main__':
    app.run(debug=True)

# create_db()