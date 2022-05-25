from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_ckeditor import CKEditorField

class SignIn(FlaskForm):
    firstname = StringField("Firstname", validators=[DataRequired()])
    lastname = StringField("Lastname", validators=[DataRequired()])
    mail = StringField("E-mail", validators=[DataRequired()])
    password_hash1 = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message='Password must match!')])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField('Submit')

class LogIn(FlaskForm):
    mail = StringField("Mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField('Submit')

art_types = [('Pieniądze w praktyce', 'Pieniądze w praktyce'), ('Ważne pojęcia', 'Ważne pojęcia'), ('Historia pieniądza', 'Historia pieniądza'), ('Ciekawostki', 'Ciekawostki')]
class AddArticle(FlaskForm):
    name = StringField("Tytuł artykułu", validators=[DataRequired()])
    subtitle = StringField("Podtytuł artykułu", validators=[DataRequired()])
    type = SelectField(u'Klasyfikacja', choices=art_types)
    content = CKEditorField('Treść artykułu', validators=[DataRequired()])
    img = FileField('')
    submit = SubmitField('Dodaj')

class EditMemberInfo(FlaskForm):
    name = StringField(validators=[DataRequired()])
    description = StringField()
    img = FileField()

class SearchArticle(FlaskForm):
    name = StringField("Szukaj po tytule artykułu...")
    submit = SubmitField()
    