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
	busqueda_form = forms.Busqueda(request.form)
	return render_template('index.html', form = busqueda_form)

@app.route('/dashboard')
def dashboard():
    user = User.query.filter_by(username = session['username']).first()

    return render_template('dashboard.html', username = session['username'],
		   email = user.email, nombre = user.first_name,
		   apellido = user.last_name, rol = session['rol'])

@app.route('/dashboardAdmin')
def dashboardAdmin():
	user = User.query.filter_by(username = session['username']).first()

	return render_template('dashboardAdmin.html',username = session['username'],
		   email = user.email, nombre = user.first_name,
		   apellido = user.last_name, rol = session['rol'])


@app.route('/user')
def listaU():
	users=Rol.query.join(UserRol, User).add_columns(Rol.code, User.id,
	                      User.username,User.email, User.created_date).filter_by(activo=1).all()
	return render_template('usuarios.html', users = users)

@app.route('/userEmail', methods =['GET','POST'])
def userEmail():
    busqueda_form = forms.Busqueda(request.form)
    if request.method == 'POST' and busqueda_form.validate():
		email = busqueda_form.email.data
		user=Rol.query.join(UserRol, User).add_columns(Rol.code, User.id,
		                  User.username,User.email, User.created_date).\
						  filter_by(email = email)
		return render_template('usuarios.html', users = user)
    return redirect(url_for('index'))


@app.route('/auth/<username>/<password>/<service>')
def autenticacion(username, password, service):
    user = UserService.query.filter_by(username = username).first()
    if user is not None and user.verify_password(password):
        return 'True'
    else:
	    return 'False'

@app.route('/rol')
def listaR():
	roles = Rol.query.all()
	return render_template('roles.html', roles = roles)


@app.route('/service')
def listaS():
	services = Service.query.all()
	return render_template('servicios.html', services = services)


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

            if rol.code == 'ADMINISTRADOR':
                    return render_template('dashboardAdmin.html', username = username,
                         email = user.email, nombre = user.first_name,
					     apellido = user.last_name, rol = session['rol'])
            else:
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
	return redirect(url_for('index'))

@app.route('/editar', methods=['GET','POST'])
def editar():
	edit_form = forms.EditForm(request.form)
	user1 = User.query.filter_by(id=session['user_id']).first()
	if request.method == 'POST' and edit_form.validate():

		user = User.query.get_or_404(session['user_id'])
		user.username = edit_form.username.data
		user.email = edit_form.email.data
		user.first_name = edit_form.first_name.data
		user.last_name = edit_form.last_name.data

		db.session.add(user)
		db.session.commit()


		success_message = 'Cambios realizados!'
		flash(success_message)

		return redirect(url_for('dashboard'))

	return render_template('editar.html', form = edit_form,
	                        username=session['username'],email = session['email'],
							nombre = user1.first_name, apellido = user1.last_name)


@app.route('/register',methods=['GET','POST'])
def register():
	register_form = forms.RegisterForm(request.form)
	if request.method == 'POST' and register_form.validate():
		user = User(register_form.username.data,
		            register_form.first_name.data,
					register_form.last_name.data,
					register_form.email.data,
					register_form.password.data,1)

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
                    create_form.password.data,1)

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
        return redirect(url_for('dashboardAdmin'))
    return render_template('createRol.html', form= createRol_form)


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


@app.route('/buscarRol', methods=['GET','POST'])
def buscarRol():
 	buscaRol_form = forms.BuscaRol(request.form)
	editaRol_form = forms.EditaRol(request.form)
 	if request.method == 'POST':
 		rol_id = buscaRol_form.rol.data
		rol = Rol.query.filter_by(id = rol_id).first()
		return render_template('editarRol.html', form = editaRol_form, name = rol.name, code = rol.code)
	return render_template('buscarRol.html', form = buscaRol_form)

@app.route('/editarRol', methods=['GET','POST'])
def editarRol():
	editaRol_form = forms.EditaRol(request.form)
	if request.method == 'POST' and editaRol_form.validate():
		rol1 = Rol.query.filter_by(name = editaRol_form.name.data).first()
		rol = Rol.query.get_or_404(rol1.id)

        rol.name = editaRol_form.name.data
        rol.code = editaRol_form.code.data
        db.session.add(rol)
        db.session.commit()


        success_message = 'Cambios realizados!'
        flash(success_message)
        return render_template('dashboardAdmin.html')
	return redirect(url_for('buscarRol'))

@app.route('/buscarUsuario', methods=['GET','POST'])
def buscarUsuario():
	buscaUsuario_form = forms.BuscaUsuario(request.form)
	editarUsuario_form = forms.EditaUsuario(request.form)
	if request.method == 'POST':
		user = User.query.filter_by(id = buscaUsuario_form.username.data).first()
		return render_template('editarUsuario.html', form = editarUsuario_form,username = user.username,
		                       email = user.email, nombre = user.first_name, apellido = user.last_name)

	return render_template('buscarUsuario.html', form = buscaUsuario_form)

@app.route('/editarUsuario', methods = ['GET','POST'])
def edditarUsuario():
	editarUsuario_form = forms.EditaUsuario(request.form)
	if request.method == 'POST' and editarUsuario_form.validate():
		user1 = User.query.filter_by(username = editarUsuario_form.username.data).first()
		user = User.query.get_or_404(user1.id)

		user.username = editarUsuario_form.username.data
		user.email = editarUsuario_form.email.data
		user.first_name = editarUsuario_form.first_name.data
		user.last_name = editarUsuario_form.last_name.data

		db.session.add(user)
		db.session.commit()

		success_message = 'Cambios realizados'
		flash(success_message)
		return render_template('dashboardAdmin.html')
	return redirect(url_for('buscarUsuario'))

@app.route('/buscarUsuarioRol', methods=['GET','POST'])
def buscarUsuarioRol():
	buscaUsuario_form = forms.BuscaUsuario(request.form)
	revocarRol_form = forms.RevocaRol(request.form)
	if request.method == 'POST':
		user = User.query.filter_by(id = buscaUsuario_form.username.data).first()
		rol = Rol.query.join(UserRol, User).add_columns(Rol.code).filter_by(id=user.id).first()
		return render_template('revocarRol.html', form = revocarRol_form,username = user.username,
		                       rol = rol.code)

	return render_template('buscarUsuario.html', form = buscaUsuario_form)

@app.route('/revocarRol', methods=['GET','POST'])
def revocarRol():
	revocarRol_form = forms.RevocaRol(request.form)
	if request.method == 'POST' and revocarRol_form.validate():
		user1 = User.query.filter_by(username = revocarRol_form.username.data).first()
		userrol1 = UserRol.query.filter_by(user_id = user1.id).first()
		userrol = UserRol.query.get_or_404(userrol1.id)

		userrol.finished_by = session['username']
		userrol.finished_at =  datetime.datetime.now()
		userrol.finished_reason = revocarRol_form.razon.data
		userrol.comment = revocarRol_form.comentario.data

		db.session.add(userrol)
		db.session.commit()
		success_message = 'Rol revocado correctamente'
		flash(success_message)
		return redirect (url_for('dashboardAdmin'))

	return redirect(url_for('buscarUsuarioRol'))

@app.route('/buscarUsuarioRol2', methods=['GET','POST'])
def buscarUsuarioRol2():
	buscaUsuario_form = forms.BuscaUsuario(request.form)
	asignaRol_form = forms.AsignaRol(request.form)
	if request.method == 'POST':
		user = User.query.filter_by(id = buscaUsuario_form.username.data).first()
		return render_template('asignaRol.html', form = asignaRol_form , username = user.username)
	return render_template('buscarUsuario.html', form = buscaUsuario_form)

@app.route('/asignaRol', methods =['GET','POST'])
def asignaRol():
	asignaRol_form = forms.AsignaRol(request.form)
	if request.method == 'POST' and asignaRol_form.validate():
		user = User.query.filter_by(username = asignaRol_form.username.data).first()
		ur = UserRol(asignaRol_form.rol.data, user.id ,
		                  session['username'])
		db.session.add(ur)
		db.session.commit()

		success_message = 'Rol asignado'
		flash(success_message)
		return redirect(url_for('dashboardAdmin'))
	return redirect(url_for('buscarUsuarioRol2'))

@app.route('/eliminarUsuario', methods=['GET','POST'])
def eliminarUsuario():
	eliminaUsuario_form = forms.EliminaUsuario(request.form)
	if request.method == 'POST':
		user = User.query.get_or_404(eliminaUsuario_form.username.data)
		user.activo = 0

		db.session.add(user)
		db.session.commit()

		success_message = 'Usuario eliminado'
		flash(success_message)
		return redirect(url_for('dashboardAdmin'))
	return render_template('eliminarUsuario.html', form=eliminaUsuario_form)

@app.route('/buscarServicio', methods=['GET','POST'])
def buscarServicio():
 	buscaServicio_form = forms.BuscaServicio(request.form)
	editaServicio_form = forms.EditaServicio(request.form)
 	if request.method == 'POST':
 		service_id = buscaServicio_form.servicio.data
		service = Service.query.filter_by(id = service_id).first()
		return render_template('editarServicio.html', form = editaServicio_form, name = service.name)
	return render_template('buscaServicio.html', form = buscaServicio_form)

@app.route('/editarServicio', methods=['GET','POST'])
def editarServicio():
	editaServicio_form = forms.EditaServicio(request.form)
	if request.method == 'POST' and editaServicio_form.validate():
		service1 = Service.query.filter_by(name = editaServicio_form.name.data).first()
		print service1.id
		service = Service.query.get_or_404(service1.id)

		service.name = editaServicio_form.name.data
		db.session.add(service)
		db.session.commit()

		success_message = 'Cambios realizados'
		flash(success_message)
		return redirect(url_for('dashboardAdmin'))
	return redirect(url_for('buscarServicio'))


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
