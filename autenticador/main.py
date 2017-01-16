from flask import Flask,request,render_template,make_response,session,redirect,url_for,flash,g
from flask_wtf import CsrfProtect

from config import DevelopmentConfig
from models import db
from models import User

import json
import forms

app = Flask(__name__) #nuevo objeto
app.config.from_object(DevelopmentConfig)

csrf = CsrfProtect()

@app.before_request
def before_request():
    g.test = 'test1'
    if 'username' not in session:
        print 'El usuario necesita autenticarse'

@app.after_request
def after_request(response):
    print g.test
    return response

@app.route('/')
def index():
    print g.test
    #custome_cookie = request.cookies.get('custome_cookie','Undefined')
    #print custome_cookie
    if 'username' in session:
        username = session['username']
        print username
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    login_form = forms.LoginForm(request.form)
    if request.method == 'POST' and login_form.validate():
        username = login_form.username.data
        success_message = 'Bienvenido {}'.format(username)
        flash(success_message)
        session['username'] = login_form.username.data
    return render_template('login.html', form=login_form)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
    return redirect(url_for('login'))

@app.route('/cookie')
def cookie():
    response = make_response( render_template('cookie.html') )
    response.set_cookie('custome_cookie','Oscar')
    return response

@app.route('/comment', methods=['GET','POST'])
def comment():
    comment_form = forms.CommentForm(request.form)

    if request.method == 'POST' and comment_form.validate():
        print comment_form.username.data
        print comment_form.email.data
        print comment_form.comment.data
    else:
        print "Error en el formulario"

    return render_template('comment.html', form = comment_form)

@app.route('/ajax-login', methods=['POST'])
def ajax_login():
    print request.form
    username = request.form['username']
    response = {'status':200,'username':username, 'id':1}
    return json.dumps(response)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

if __name__ == '__main__':
    csrf.init_app(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(port = 8000) #se encarga de ejecutar el servidor
