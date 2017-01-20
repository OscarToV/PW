from flask import Flask,request,render_template,jsonify
from flask import make_response,session,redirect,url_for,flash,g
from flask_wtf import CsrfProtect
from flaskext.mysql import MySQL
import itertools

from config import DevelopmentConfig
from models import db
from models import User

import json
import forms

app = Flask(__name__) #nuevo objeto
app.config.from_object(DevelopmentConfig)
mysql = MySQL()
mysql.init_app(app)

csrf = CsrfProtect()


def dictfetchall(cursor):
	desc = cursor.description
	return [dict(itertools.izip([col[0] for col in desc],row))
			for row in cursor]

def consulta(sql):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute(sql)
	except Exception as e:
		return render_template('ErrorBD.html', error=str(e))
	return cursor

@app.before_request
def before_request():
#     g.test = 'test1'
#     if 'username' not in session:
#         print 'El usuario necesita autenticarse'
	  if 'username' in session and request.endpoint in ['login','create']:
		return redirect(url_for('index'))

# @app.after_request
# def after_request(response):
#     print g.test
#     return response

@app.route('/')
def index():
	#print g.test
	#custome_cookie = request.cookies.get('custome_cookie','Undefined')
	#print custome_cookie
	if 'username' in session:
		username = session['username']
		print username
	return render_template('index.html')

@app.route('/user')
def listaU():
	param = request.args.get('email',None)

	if param is None:
		cursor = consulta('SELECT username,email,created_date,code AS rol FROM users LEFT JOIN userrol ON userrol.user_id = users.id JOIN roles ON userrol.rol_id = roles.id')
	else:
		cursor = consulta("SELECT username,email,created_date,code AS rol FROM users LEFT JOIN userrol ON userrol.user_id = users.id JOIN roles ON userrol.rol_id = roles.id WHERE email = '{}'".format(param))

	results = dictfetchall(cursor)
	return jsonify(datos=results)

@app.route('/rol')
def listaR():
	sql = 'SELECT * FROM roles'
	cursor = consulta(sql)
	results = dictfetchall(cursor)
	return jsonify(datos=results)

@app.route('/service')
def listaS():
	sql = 'SELECT * FROM services'
	cursor = consulta(sql)
	results = dictfetchall(cursor)
	return jsonify(datos=results)


@app.route('/login', methods = ['GET', 'POST'])
def login():
	login_form = forms.LoginForm(request.form)
	if request.method == 'POST' and login_form.validate():
		username = login_form.username.data
		password = login_form.password.data

		user = User.query.filter_by(username = username).first()
		rol = consulta('SELECT code AS rol FROM users JOIN userrol ON userrol.id = users.id JOIN roles ON userrol.id = roles.id WHERE users.id={}'.format(user.id))
		if user is not None and user.verify_password(password):
			success_message = 'Bienvenido {}'.format(username)
			flash(success_message)

			session['username'] = username
			session['user_id'] = user.id
			print user.id
			 

			return redirect( url_for('index') )

		else:
			error_message= 'Usuario o password no validos!'
			flash(error_message)

		session['username'] = login_form.username.data
	return render_template('login.html', form = login_form)

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

# @app.route('/ajax-login', methods=['POST'])
# def ajax_login():
#     print request.form
#     username = request.form['username']
#     response = {'status':200,'username':username, 'id':1}
#     return json.dumps(response)

@app.route('/create', methods=['GET','POST'])
def create():
	create_form = forms.CreateForm(request.form)
	if request.method == 'POST' and create_form.validate():

		user = User(create_form.username.data,
					create_form.password.data,
					create_form.email.data)

		db.session.add(user)
		db.session.commit()

		success_message = 'Usuario registrado en la base de datos'
		flash(success_message)
	return render_template('create.html', form=create_form)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html')

if __name__ == '__main__':
	csrf.init_app(app)
	db.init_app(app)
	with app.app_context():
		db.create_all()
	app.run(port = 8000) #se encarga de ejecutar el servidor
