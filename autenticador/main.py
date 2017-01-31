from flask import Flask,request,render_template,jsonify
from flask import make_response,session,redirect,url_for,flash,g
from flask_wtf import CSRFProtect
from flaskext.mysql import MySQL
from flask_bootstrap import Bootstrap
from flask_uuid import FlaskUUID
import itertools
import uuid
import datetime

from config import DevelopmentConfig
from models import db
from models import User, Rol, UserRol, Service, UserService, Session, Query

import json
import forms

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
mysql = MySQL()
mysql.init_app(app)
FlaskUUID(app)
Bootstrap(app)

csrf = CSRFProtect()


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
	if 'username' not in session and request.endpoint in ['editar','create','dashboard','createService','createRol','asignaRol','createSA']:
		error_message= 'Necesita autenticarse!'
		flash(error_message)
		return redirect(url_for('login'))

	if 'username' in session and request.endpoint in ['login','register']:
		return redirect(url_for('dashboard'))

	if 'username' in session and request.endpoint in ['create','createService','createRol','asignaRol'] and session['rol'] != 'ADMINISTRADOR':
	    return redirect(url_for('index'))


@app.route('/')
def index():
	if 'username' in session:
		username = session['username']
		print username
	return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    user = User.query.filter_by(username = session['username']).first()

    return render_template('dashboard.html', username = session['username'],
		   email = user.email, nombre = user.first_name,
		   apellido = user.last_name, rol = session['rol'])


@app.route('/user')
def listaU():
	param = request.args.get('email',None)

	if param is None:
		cursor = consulta('SELECT username,email,created_date,code AS rol FROM users LEFT JOIN userrol ON userrol.user_id = users.id JOIN roles ON userrol.rol_id = roles.id')
	else:
		cursor = consulta("SELECT username,email,created_date,code AS rol FROM users LEFT JOIN userrol ON userrol.user_id = users.id JOIN roles ON userrol.rol_id = roles.id WHERE email = '{}'".format(param))

	results = dictfetchall(cursor)
	return jsonify(datos=results)

@app.route('/auth/<username>/<password>/<service>')
def autenticacion(username, password, service):
    user = UserService.query.filter_by(username = username).first()
    if user is not None and user.verify_password(password):
        return 'True'
    else:
	    return 'False'

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
		#rol = consulta('SELECT code AS rol FROM users JOIN userrol ON userrol.id = users.id JOIN roles ON userrol.id = roles.id WHERE users.id={}'.format(user.id))
		rol = Rol.query.join(UserRol, User).add_columns(Rol.code).filter_by(id=user.id).first()
		if user is not None and user.verify_password(password):
			success_message = 'Bienvenido {}'.format(username)
			flash(success_message)

			session['Finicio'] = datetime.datetime.now()
			session['username'] = username
			session['user_id'] = user.id
			session['rol'] = rol.code
			session['sid'] = uuid.uuid4()
			session['email'] = user.email


			return render_template('dashboard.html', username = username,
				       email = user.email, nombre = user.first_name,
					   apellido = user.last_name, rol = session['rol'])

		else:
			error_message= 'Usuario o password no validos!'
			flash(error_message)
	return render_template('login.html', form = login_form)

@app.route('/logout')
def logout():
	if 'username' in session:
		Ftermina = datetime.datetime.now()


        s = Session(session['sid'], session['email'], session['rol'],
		session['Finicio'], Ftermina)
        db.session.add(s)
        db.session.commit()

        session.pop('username')
        session.pop('user_id')
        session.pop('rol')
        session.pop('Finicio')
        session.pop('sid')
        session.pop('email')
	return redirect(url_for('login'))

@app.route('/editar', methods=['GET','POST'])
def editar():
    edit_form = forms.EditForm(request.form)

    if request.method == 'POST' and edit_form.validate():

        user = User.query.get_or_404(session['user_id'])
        user.username = edit_form.username.data
        user.email = edit_form.email.data

        db.session.add(user)
        db.session.commit()


        success_message = 'Cambios realizados!'
        flash(success_message)

        return redirect(url_for('index'))

    return render_template('editar.html', form = edit_form)


@app.route('/register',methods=['GET','POST'])
def register():
	register_form = forms.RegisterForm(request.form)
	if request.method == 'POST' and register_form.validate():
		user = User(register_form.username.data,
		            register_form.first_name.data,
					register_form.last_name.data,
					register_form.email.data,
					register_form.password.data)

		username = register_form.username.data
		db.session.add(user)
		db.session.commit()

		nu = User.query.filter_by(username = username).first()
		ur = UserRol(2,nu.id, username)
		db.session.add(ur)
		db.session.commit()

		success_message = 'Usuario registrado'
		flash(success_message)
	return render_template('register.html', form = register_form)

@app.route('/create', methods=['GET','POST'])
def create():
   create_form = forms.CreateForm(request.form)
   if request.method == 'POST' and create_form.validate():

       user = User(create_form.username.data,
                    create_form.first_name.data,
                    create_form.last_name.data,
					create_form.email.data,
                    create_form.password.data)

       username = create_form.username.data

       db.session.add(user)
       db.session.commit()
       nu = User.query.filter_by(username = username).first()
       ur = UserRol(create_form.rol.data, nu.id, session['username'])

       db.session.add(ur)
       db.session.commit()

       success_message = 'Usuario registrado en la base de datos'
       flash(success_message)

   return render_template('create.html', form=create_form)


@app.route('/createService', methods=['GET', 'POST'])
def createService():
	createService_form = forms.CreateServiceForm(request.form)
	if request.method == 'POST' and createService_form.validate():

         service = Service(createService_form.name.data)
         db.session.add(service)
         db.session.commit()

         success_message = 'Servicio registrado!'
         flash(success_message)
	return render_template('createService.html', form= createService_form)

@app.route('/createRol', methods=['GET','POST'])
def createRol():
    createRol_form = forms.CreateRolForm(request.form)
    if request.method == 'POST' and createRol_form.validate():

        rol = Rol(createRol_form.name.data,createRol_form.code.data)
        db.session.add(rol)
        db.session.commit()
        success_message = 'Rol registrado!'
        flash(success_message)
    return render_template('createRol.html', form= createRol_form)

@app.route('/asignaRol',methods=['GET','POST'])
def asignaRol():
    asignaRol_form = forms.AsignaRol(request.form)
    if request.method == 'POST':
        rol = asignaRol_form.rolNuevo.data
        print rol
    return render_template('asignaRol.html', form =asignaRol_form)

@app.route('/createSA', methods=['GET','POST'])
def createSA():
	createSA_form = forms.CreateSAForm(request.form)
	if request.method == 'POST' and createSA_form.validate():

		userservice =  UserService(session['user_id'],
		                           createSA_form.service.data,
                                   createSA_form.username.data,
							       createSA_form.password.data,
							       createSA_form.hint.data)

		db.session.add(userservice)
		db.session.commit()
		success_message = 'Servicio de autenticacion creado'
		flash(success_message)
	return render_template('createSA.html', form=createSA_form)

@app.route('/SA', methods=['GET','POST'])
def SA():
    login_SA_form = forms.SAForm(request.form)
    if request.method == 'POST' and login_SA_form.validate():
        username = login_SA_form.username.data
        password = login_SA_form.password.data
        service = login_SA_form.service.data
        user = UserService.query.filter_by(username = username).first()

        if user is not None and user.verify_password(password):
			success_message = 'Bienvenido {}'.format(username)
			flash(success_message)

			return render_template('service.html')

        else:
			error_message = 'Datos incorrectos!... Pista:  {}'.format(user.hint)
			flash(error_message)

    return render_template('SA.html', form = login_SA_form)

@app.route('/query/<name>')
def consultor(name):
    consul = Query.query.filter_by(name= name).first()
    cursor = consulta(consul.sql)
    results = dictfetchall(cursor)

    return jsonify(datos=results)





@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html')

if __name__ == '__main__':
	csrf.init_app(app)
	db.init_app(app)
	with app.app_context():
		db.create_all()
	app.run(port = 8000) #se encarga de ejecutar el servidor
