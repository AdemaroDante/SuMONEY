from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_ckeditor import CKEditorField

class SignIn(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    firstname = StringField("Firstname", validators=[DataRequired()])
    lastname = StringField("Lastname", validators=[DataRequired()])
    mail = StringField("E-mail", validators=[DataRequired()])
    password_hash1 = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message='Password must match!')])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField('Submit')

class LogIn(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Submit')

class AddArticle(FlaskForm):
    name = StringField("Tytuł artykułu", validators=[DataRequired()])
    subtitle = StringField("Podtytuł artykułu", validators=[DataRequired()])
    type = StringField("Typ", validators=[DataRequired()])
    content = CKEditorField('Treść artykułu', validators=[DataRequired()])
    submit = SubmitField('Dodaj')
    