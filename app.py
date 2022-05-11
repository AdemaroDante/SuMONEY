from db import db, db_init
from flask import Flask, flash, redirect, render_template, url_for
from flask_ckeditor import CKEditor, CKEditorField
from flask_login import LoginManager, current_user, login_manager, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from forms import AddArticle, LogIn, SearchArticle, SignIn, EditMemberInfo
from models import Articles, Users, Members
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import uuid as uuid
import os
import datetime
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = "SkuMONEY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/database/main.sqlite3'
UPLOAD_FOLDER = 'static/img/articles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
migrate = Migrate(app, db)
db_init(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
ckeditor = CKEditor(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# -------------------- Views -------------------- 
# Main page 
@app.route('/', methods=['GET'])
def home():
    art = Articles.query.order_by(Articles.id.desc()).limit(6).all()
    return render_template('index.html', art=art)

# All articles
@app.route('/artykuły', methods=['GET', 'POST'])
def articles():
    form = SearchArticle()
    art = Articles.query.all()
    if form.validate_on_submit():
        art = Articles.query.filter(Articles.name.like(f"%{form.name.data}%")).all()
        if form.name.data == '':
            art = Articles.query.all()
    return render_template('articles.html', art=art, form=form)

# List of articles with some type
@app.route('/artykuły/kategoria=<type>', methods=['GET', 'POST'])
def type_articles(type):
    form = SearchArticle()
    article = Articles.query.filter(Articles.type == type).all()
    if form.validate_on_submit():
        art = Articles.query.filter(Articles.name.like(f"%{form.name.data}%")).all()
        if form.name.data == '':
            art = Articles.query.all()
    return render_template('articles.html', art=article, form=form)

# Single article page
@app.route('/artykuł/<article_name>', methods = ['GET', 'POST'])
def article(article_name):
    article = Articles.query.filter_by(name=article_name).first()
    if not article:
        return 'Not found..!', 404
    return render_template('article.html', article = article)

# About page
@app.route('/o-nas', methods=['GET'])
def about():
    member = Members.query.all()
    return render_template('about.html', member=member)

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LogIn()
    # Form validate
    if form.validate_on_submit():
        user = Users.query.filter_by(mail = form.mail.data).first()
        if user:
            # Checking hash:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash(f'Zalogowano jako {current_user.firstname} {current_user.lastname}')
                return redirect(url_for('admin'))

            else:
                flash('Złe hasło!')
        else:
            flash('Zły login!')

    if current_user.is_authenticated:
        return redirect(url_for('admin'))

    return render_template('admin/login.html', form = form)

# Logout function
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('Wylogowano!')
    return redirect(url_for('home'))

# Admin dashboard
@app.route('/admin', methods = ['GET', 'POST'])
@login_required
def admin():
    article = Articles.query.all()
    return render_template('admin/index.html', article=article)

# Admin - articles
@app.route('/admin/artykuły', methods = ['GET', 'POST'])
@login_required
def admin_articles():
    article = Articles.query.all()
    return render_template('admin/articles.html', article=article)

# Admin - add article
@app.route('/admin/artykuły/dodaj', methods = ['GET', 'POST'])
@login_required
def admin_add_article():
    form = AddArticle()

    if form.validate_on_submit():
        name = form.name.data
        subtitle = form.subtitle.data
        type = form.type.data
        content = form.content.data
        if form.img.data:
            img = form.img.data
            img_filename = secure_filename(img.filename)
            img_name = str(uuid.uuid1()) + "_" + img_filename
            img.save(os.path.join(app.config['UPLOAD_FOLDER'], img_name))
            img = img_name
        else:
            img = '../default_article_image.jpg'
        added_by = str(f"{current_user.firstname} {current_user.lastname}")

        new_article = Articles(name=name, subtitle=subtitle, type=type, content=content, img=img, added_by=added_by, date=datetime.datetime.now())
        db.session.add(new_article)
        db.session.commit()

        form.name.data, form.subtitle.data, form.type.data, form.content.data = '', '', '', ''
        flash('Dodano artykuł!')
        
    return render_template('admin/edit_article.html', form=form, url_='dodaj', editing_article=None)

# Admin - edit article
@app.route('/admin/artykuły/edytuj/<int:id>', methods = ['GET', 'POST'])
@login_required
def admin_edit_article(id):
    editing_article = Articles.query.get_or_404(id)
    form = AddArticle()

    if form.validate_on_submit():
        editing_article.name = form.name.data 
        editing_article.subtitle = form.subtitle.data
        editing_article.type = form.type.data
        editing_article.content = form.content.data
        editing_article.img = form.img.data
        editing_article.date = datetime.datetime.now()
        editing_article.added_by = str(f"{current_user.firstname} {current_user.lastname}")
        try:
            db.session.commit()
            flash('Zapisano zmiany!')
        except:
            flash('Nie można zapisać zmian!')
        
    form.content.data = editing_article.content
    form.img.data = editing_article.img
    return render_template('admin/edit_article.html', form=form, url_=f'edytuj/{id}', editing_article=editing_article)

# Delete article
@app.route('/admin/artykuły/usuń_artykuł/<int:id>', methods=['POST', 'GET'])
@login_required
def admin_delete_article(id):
    article_to_delete = Articles.query.get_or_404(id)

    try:
        db.session.delete(article_to_delete)
        db.session.commit()
        flash('Usunięto artykuł!')
        return redirect(url_for('admin_articles'))
    except:
        flash("Nie można usunąć artykułu!")
        return redirect(url_for('admin_articles'))

# Admin - edit /o-nas content
@app.route('/admin/edytuj-treści/o-nas', methods=['GET', 'POST'])
@login_required
def edit_about():
    flash('Ta funkcja nie jest jeszcze dostępna!')
    return redirect(url_for('admin'))

# Admin - edit /kontakt content
@app.route('/admin/edytuj-treści/stopka', methods=['GET', 'POST'])
@login_required
def edit_footer():
    flash('Ta funkcja nie jest jeszcze dostępna!')
    return redirect(url_for('admin'))

# Admin - users
@app.route('/admin/users', methods = ['GET', 'POST'])
@login_required
def admin_users():
    user = Users.query.all()
    return render_template('admin/users.html', user=user)

# Create new user page
@app.route('/admin/register', methods=['GET', 'POST'])
#@login_required
def admin_register_user():
    form = SignIn()
    if form.validate_on_submit():
        other_mail = Users.query.filter_by(mail = form.mail.data).first()
        if other_mail is None:
            # Hashing password:
            hashed_pw = generate_password_hash(form.password_hash1.data, "sha256")
            new_user = Users(firstname=form.firstname.data, lastname=form.lastname.data, mail=form.mail.data, password_hash=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            form.firstname.data, form.lastname.data, form.mail.data, form.password_hash1.data, form.password_hash2.data = '', '', '', '', ''
            flash('Dodano użytkownika!')
        else:
            flash('Konto z takim mailem już istnieje!')
    
    return render_template('admin/register.html', form=form)

# Delete user
@app.route('/admin/delete_user_<int:id>', methods=['POST', 'GET'])
@login_required
def admin_delete_user(id):
    user_to_delete = Users.query.get_or_404(id)

    if user_to_delete.mail == 'jozek.kasprzycki@gmail.com':
        flash('Nie możesz usunąć twórcy tego serwisu 🤦')
        return redirect(url_for('admin_users'))
    if user_to_delete.mail == current_user.mail:
        flash('Nie możesz sam_a się usunąć 🤦')
        return redirect(url_for('admin_users'))

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('Usunięto pomyślnie!')
    except:
        flash("ERROR 500, nie można usunąć użytkownika!")

    return redirect(url_for('admin_users'))

# Error 404 page
@app.errorhandler(404)
def not_found(e):
  return render_template('404.html')


if __name__ == '__main__':
   app.run(debug = True)
