from wsgiref import validate
from flask import Flask, render_template, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from db import db_init, db
from models import Articles, Users
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from forms import LogIn, SignIn, AddArticle, SearchArticle
from flask_login import login_user, LoginManager, login_manager, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor, CKEditorField
import difflib

app = Flask(__name__)
app.config['SECRET_KEY'] = "SkuMONEY"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///static/database/main.sqlite3'
db_init(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

ckeditor = CKEditor(app)

# ---------- Views ----------
# Main page 
@app.route('/', methods=['GET'])
def home():
    articles = Articles.query.all()
    latest = 0
    for articles in articles:
        latest += 1

    class banner():
        bg_ban1 = Articles.query.get(latest)
        bg_ban2 = Articles.query.get(latest-1)
        sm_ban3 = Articles.query.get(latest-2)
        sm_ban4 = Articles.query.get(latest-3)
        sm_ban5 = Articles.query.get(latest-4)
        sm_ban6 = Articles.query.get(latest-5)

    return render_template('index.html', banner = banner, latest = latest)

# List of articles
@app.route('/artykuły', methods=['GET', 'POST'])
def articles():
    form = SearchArticle()
    article = Articles.query.all()

    if form.validate_on_submit():
        article = Articles.query.filter(Articles.name.like(f"%{form.name.data}%")).all()

        if form.name.data == '':
            article = Articles.query.all()
        
    return render_template('articles.html', article=article, form=form)

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
    return render_template('about.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LogIn()
    # Form validate
    if form.validate_on_submit():
        user = Users.query.filter_by(username = form.username.data).first()
        if user:
            # Checking hash:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash(f'Zalogowano jako {current_user.username}')
                return redirect(url_for('admin'))

            else:
                flash('Złe hasło!')
        else:
            flash('Zły login!')

    if current_user.is_authenticated:
        return redirect(url_for('admin'))

    return render_template('login.html', form = form)

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
    return render_template('admin/index.html')

# Admin - articles
@app.route('/admin/artykuły', methods = ['GET', 'POST'])
@login_required
def admin_articles():
    article = Articles.query.all()
    return render_template('admin_articles.html', article=article)

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
        added_by = str(f"{current_user.firstname} {current_user.lastname}")

        new_article = Articles(name=name, subtitle=subtitle, type=type, content=content, added_by=added_by)

        db.session.add(new_article)
        db.session.commit()

        form.name.data, form.subtitle.data, form.type.data, form.content.data, current_user.username = '', '', '', '', ''

        flash('Dodano artykuł!')
        
    return render_template('admin/edit_article.html', form=form)

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
        editing_article.added_by = str(f"{current_user.firstname} {current_user.lastname}")
        try:
            db.session.commit()
            flash('Zapisano zmiany!')
        except:
            flash('Nie można zapisać zmian!')
    form.content.data = editing_article.content
    return render_template('admin/edit_article.html', form=form, editing_article=editing_article)

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




# Admin - users
@app.route('/admin/users', methods = ['GET', 'POST'])
@login_required
def admin_users():
    user = Users.query.all()
    return render_template('admin/users.html', user=user)

# Create new user page
@app.route('/admin/add_user', methods=['GET', 'POST'])
# @login_required
def add_user():
    form = SignIn()
    if form.validate_on_submit():
        other_user = Users.query.filter_by(username = form.username.data).first()
        if other_user is None:
            other_mail = Users.query.filter_by(mail = form.mail.data).first()
            if other_mail is None:
                # Hashing password:
                hashed_pw = generate_password_hash(form.password_hash1.data, "sha256")
                new_user = Users(username=form.username.data, firstname=form.firstname.data, lastname=form.lastname.data, mail=form.mail.data, password_hash=hashed_pw)
                db.session.add(new_user)
                db.session.commit()
                form.username.data, form.firstname.data, form.lastname.data, form.mail.data, form.password_hash1.data, form.password_hash2.data = '', '', '', '', '', ''
                flash('Dodano użytkownika!')

            else:
                flash('Konto z takim mailem już istnieje!')
        else:
            flash("Ten użytkownik już istnieje!")
    
    return render_template('admin/add_user.html', form=form)

# Delete user
@app.route('/admin/delete_user_<int:id>', methods=['POST', 'GET'])
@login_required
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)

    if user_to_delete.username == 'SuperAdmin':
        flash('You cant delete webpage creator 🤦')
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
