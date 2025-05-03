from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, DecimalField, SelectField, SubmitField, FileField
from flask_wtf.file import FileRequired
from wtforms.validators import DataRequired, Email, Length


class Registration(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=4, max=20)],
                           render_kw={'placeholder': 'Имя пользователя', 'class': 'input', 'type': 'username'})
    email = StringField(validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'Почта', 'class': 'input', 'type': 'email'})
    password = PasswordField(validators=[DataRequired(), Length(min=8)],
                             render_kw={'placeholder': 'Пароль', 'class': 'password', 'type': 'password'})
    submit = SubmitField('Присоединиться')


class Login(FlaskForm):
    username = StringField(validators=[DataRequired(), Length(min=4, max=20)],
                           render_kw={'placeholder': 'Имя пользователя', 'class': 'input', 'type': 'username'})
    password = PasswordField(validators=[DataRequired(), Length(min=8)],
                             render_kw={'placeholder': 'Пароль', 'class': 'password', 'type': 'password'})
    submit = SubmitField('Войти')


class UploadItem(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    content = TextAreaField('Содержание', validators=[DataRequired()])
    content_file = FileField()
    price = DecimalField('Цена', validators=[DataRequired()], places=2)
    category = SelectField('Категория', choices=[('', 'Выберите категорию')], validators=[DataRequired()])
    subcategory = SelectField('Подкатегория', choices=[('', 'Выберите подкатегорию')], validators=[DataRequired()])
    photo = FileField()
    submit = SubmitField('Загрузить')