from flask import Flask,request,render_template,make_response,session,redirect,url_for
from flask_wtf import CsrfProtect

import forms

app = Flask(__name__) #nuevo objeto
app.secret_key = 'my_secret_key'
csrf = CsrfProtect(app)

@app.route('/')
def index():
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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
if __name__ == '__main__':
	app.run(debug = True, port = 8000) #se encarga de ejecutar el servidor
