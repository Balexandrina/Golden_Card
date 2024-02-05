import sqlite3
import os
from turtle import title
from flask import Flask, render_template, request, g, flash, abort, session, url_for, redirect, make_response
from FDataBase import FDataBase
from BlogDB import BlogDataBase
from werkzeug.security import generate_password_hash, check_password_hash # кодирование данных
from flask_login import LoginManager, login_user, login_required, logout_user, current_user # управляет процессом авторизации
from UserLogin import UserLogin

DATABASE = 'site.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k' 
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path,'site.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login' 
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success" # категория мгновенного сообщения

@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

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

dbase = None
@app.before_request
def before_request():
    '''Установление соединения с БД перед выполнением запроса'''
    global dbase
    db = get_db()
    dbase = FDataBase(db)

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
@login_required
def get_post(post_id):
    db = get_db()
    post = db.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    db.close()
    return render_template('post.html', post=post) # рендерим HTML-шаблон и передаём туда полученный пост

@app.route('/login', methods=["POST", "GET"])
def login():
    '''Обработчик для авторизации пользователя'''
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email']) 
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user) 
            rm = True if request.form.get('remainme') else False 
            login_user(userlogin, remember = rm) 
            return redirect(request.args.get("next") or url_for("profile")) 
        flash("Неверная пара логин/пароль", "error")
    return render_template('login.html', title = 'Авторизация')

@app.route('/register', methods = ['POST', 'GET'])
def register(): 
    if request.method == "POST": 
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
            and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']: 
            hash = generate_password_hash(request.form['psw']) # кодируем пароль
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res: 
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login')) 
            else:
                flash(f"Пользователь с email {request.form['email']} уже существует", "error")
        else:
            flash("Неверно заполнены поля", "error")
        
    return render_template('register.html', title = 'Регистрация')

@app.route('/logout')
@login_required
def logout():
    logout_user() 
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

@app.route('/profile')
@login_required 
def profile():
    return render_template('profile.html', title = 'Профиль')

@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app) 
    if not img: 
        return ""
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png' 
    return h 

@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file'] 
        if file and current_user.verifyExt(file.filename): 
            try:
                img = file.read() # чтение данных из файла
                res = dbase.updateUserAvatar(img, current_user.get_id()) 
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")
    return redirect(url_for('profile'))

@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена")

if __name__ == '__main__':
    app.run(debug=True)

# create_db()
# insert_posts()
