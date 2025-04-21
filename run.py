from flask import Flask, render_template
import oauth
import forms
import os


app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/register')
def sign_in():
    return render_template('auth/register.html', form=forms.Registration())

@app.route('/login')
def sign_up():
    return render_template('auth/login.html', form=forms.Login())

if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)