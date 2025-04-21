from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
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