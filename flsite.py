import sqlite3
import os
from turtle import title
from flask import Flask, render_template, request, g, flash, abort
from FDataBase import FDataBase
from BlogDB import BlogDataBase

DATABASE = 'site.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'  

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path,'site.db')))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn 

def create_db():
    db = connect_db()
    db.execute('CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, img BLOB NOT NULL, img_name TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS review (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, text TEXT NOT NULL, time integer NOT NULL)')

# функция для вставки постов в блог
def insert_posts():
    db = connect_db()
    dbase = BlogDataBase(db)
    dbase.insert_blob(1, 'Итоги выставки "Сибирская продовольственная неделя"', 'Итак: итоги выставки "Сибирская продовольственная неделя", для нашей мастерской, оказались позитивными.', "novosib.jpg", "novosib.jpg")
    dbase.insert_blob(2, "Линейка шоколада «Мой Новосибирск»", "Запущена в разработку линейка шоколада «Мой Новосибирск», состоящая из пяти плиток с рельефными изображениями живописных видов Новосибирска." ,"blog_novosib.jpg", "blog_novosib.jpg")
    dbase.insert_blob(3, "Выставка в Екатеринбурге", "В ноябре 2021 года наша компания участвовала в в международной выставке InterFoodUral2021 в составе делегации Кузбасса." , "main.jpg", "main.jpg")   

def get_db(): # Соединение с БД, если оно еще не установлено
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error): # Закрываем соединение с БД, если оно было установлено
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.before_first_request
def before_first_request():
    create_db()

@app.route("/")
def index():
    return render_template('index.html', title='Главная')

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
 
    if request.method == "POST": # если данные от формы пришли
        if len(request.form['name']) > 2 and len(request.form['post']) > 2: # простая проверка на количество символов в имени и отзыве
            res = dbase.addReview(request.form['name'], request.form['post'])
            if not res:
                flash('Ошибка добавления отзыва', category = 'error')
            else:
                flash('Благодарим за отзыв!', category='success')
        else:
            flash('Ошибка добавления отзыва', category='error')
 
    return render_template('add_feedback.html', menu = dbase.getMenu(), title="Отзывы", posts = dbase.getPostsAnonce()) 

@app.route('/blog')
def blog():
    db = connect_db()
    posts = db.execute('SELECT * FROM posts').fetchall()
    db.close()
    return render_template('blog.html', title='Блог', posts = posts)

@app.route('/<int:post_id>')
def get_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    db.close()
    return render_template('post.html', post=post) # рендерим HTML-шаблон и передаём туда полученный пост

@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена")

if __name__ == '__main__':
    app.run(debug=True)

# create_db()
# insert_posts()
