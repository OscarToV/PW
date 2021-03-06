from wtforms import Form, StringField, TextField, validators, HiddenField,PasswordField, SelectField, TextAreaField
from wtforms.fields.html5 import EmailField
from models import User

def length_honneypot(form, field):
	if len(field.data)>0:
		raise validators.ValidationError('El campo debe estar vacio.')

class EditForm(Form):

	username = StringField('username',
			   [
				 validators.Required(message='El username es requerido!'),
				 validators.length(min=4, max=25, message='Ingrese username valido!')
               ])
	email = EmailField('Correo electronico',
			[
			  validators.Required(message='El email es requerido!'),
			  validators.Email(message='Ingrese un email valido!')
			])
	first_name = StringField('nombre',
			   [
				 validators.Required(message='El nombre es requerido!'),
				 validators.length(min=4, max=25, message='Ingrese nombre valido!')
	           ])
	last_name = StringField('apellido',
	           [
				 validators.Required(message='El apellido es requerido!'),
				 validators.length(min=4, max=25, message='Ingrese apellido valido!')
			   ])

	honneypot = HiddenField('',[length_honneypot])

class LoginForm(Form):
	username = StringField('username',
		  [
			validators.Required(message='El username es requerido!'),
			validators.length(min=4, max=25, message='Ingrese un username valido!')
		  ])
	password = PasswordField('Password',[validators.Required(message='El password es requerido')])


class CreateForm(Form):
	username = TextField('Username',
						[
							validators.Required(message = 'El username es requerido'),
							validators.length(min=4, max=50, message='Ingrese un username valido')
						])
	email = EmailField('Correo electronico',
						[	validators.Required(message = 'El email es requerido!.'),
							validators.Email(message='Ingre un email valido'),
							validators.length(min=4, max=50, message='Ingrese un email valido')
						])
	password = PasswordField('Password', [validators.Required(message='El password es requerido')])

	last_name = TextField('Apellido',
       [
       validators.Required(message='El apellido es requerido'),
       validators.length(min=3, max=50, message='Ingrese un apellido valido')
       ])

	first_name = TextField('Nombre',
                      [
						  validators.Required(message = 'El nombre es requerido'),
						  validators.length(min=2, max=50, message='Ingrese un nombre valido')
					  ])


	rol = SelectField('Rol', choices=[('1','ADMINISTRADOR'),('2','USUARIO')])

	def validate_username (form, field):
		username = field.data
		user = User.query.filter_by(username = username).first()
		if user is not None:
			raise validators.ValidationError('El username ya se encuentra registrado.')

class CreateServiceForm(Form):
    name = StringField('name',[
	    validators.Required(message='El nombre es requerido!'),
		validators.length(min=3, max=25, message='Ingrese un nombre valido!')
	])


class CreateRolForm(Form):
	name = StringField('name',[
	    validators.Required(message='El nombre es requerido!'),
		validators.length(min=3, max=25, message='Ingrese un nombre valido!')
	])

	code = StringField('code',[
	    validators.Required(message='El codigo es requerido!'),
		validators.length(min=3, max=25, message='Ingrese un codigo valido!')
	])

class AsignaRol(Form):
	username = StringField('Usuario', [validators.Required(message='Este campo es obligatorio')])
	rol= SelectField('Roles', choices=[('1','ADMINISTRADOR'),('2','USUARIO'),('3','INVITADO')])


class CreateSAForm(Form):
   username = StringField('Username',[
       validators.Required(message = 'El nombre es requerido!'),
	   validators.length(min=4, max=50, message='Ingrese un username valido')
   ])

   password = PasswordField('Password', [validators.Required(message='El password es requerido!')])

   hint = StringField('tip',[validators.Required(message='Este campo es obligatorio')])

   service = SelectField('Servicio', choices = [('1','FTP'),('2','Correo')])


class RegisterForm(Form):
	username = TextField('Username',
						[
							validators.Required(message = 'El username es requerido'),
							validators.length(min=4, max=50, message='Ingrese un username valido')
						])
	email = EmailField('Correo electronico',
						[	validators.Required(message = 'El email es requerido!.'),
							validators.Email(message='Ingre un email valido'),
							validators.length(min=4, max=50, message='Ingrese un email valido')
						])
	password = PasswordField('Password', [validators.Required(message='El password es requerido')])

	last_name = TextField('Apellido',
       [
       validators.Required(message='El apellido es requerido'),
       validators.length(min=3, max=50, message='Ingrese un apellido valido')
       ])

	first_name = TextField('Nombre',
                      [
						  validators.Required(message = 'El nombre es requerido'),
						  validators.length(min=2, max=50, message='Ingrese un nombre valido')
					  ])

class SAForm(Form):
	username = StringField('username',
		  [
			validators.Required(message='El username es requerido!'),
			validators.length(min=4, max=25, message='Ingrese un username valido!')
		  ])
	password = PasswordField('Password',[validators.Required(message='El password es requerido')])

	service = SelectField('Servicio', choices = [('1','FTP'),('2','Correo')])


class BuscaRol(Form):
	rol = SelectField('Rol', choices=[('1','Administrador'),('2','Usuario')])


class EditaRol(Form):
	name = StringField('nombre',[validators.Required(message='El nombre es requerido!')])
	code = StringField('codigo',[validators.Required(message='El codigo es requerido!')])

class BuscaUsuario(Form):
	username = SelectField('Usuario', choices = [('1','Oskar'),('2','chesmin'),('3','arti'),('4','cocabet')])

class EditaUsuario(Form):

	username = StringField('username',
			   [
				 validators.Required(message='El username es requerido!'),
				 validators.length(min=4, max=25, message='Ingrese username valido!')
               ])
	email = EmailField('Correo electronico',
			[
			  validators.Required(message='El email es requerido!'),
			  validators.Email(message='Ingrese un email valido!')
			])
	first_name = StringField('nombre',
			   [
				 validators.Required(message='El nombre es requerido!'),
				 validators.length(min=4, max=25, message='Ingrese nombre valido!')
	           ])
	last_name = StringField('apellido',
	           [
				 validators.Required(message='El apellido es requerido!'),
				 validators.length(min=4, max=25, message='Ingrese apellido valido!')
			   ])

	honneypot = HiddenField('',[length_honneypot])

	idU = HiddenField('',[])


class RevocaRol(Form):

	username = StringField('Username',
			   [
				 validators.Required(message='El username es requerido!'),
				 validators.length(min=4, max=25, message='Ingrese username valido!')
               ])
	rol = StringField('Rol',
			[
			  validators.Required(message='El rol es requerido!')
			])
	razon = TextAreaField('Razon',
			   [
				 validators.Required(message='Una razon es requerida!')
	           ])
	comentario = TextAreaField('Cometario')

	honneypot = HiddenField('',[length_honneypot])

class Busqueda(Form):
	email = EmailField('',
			[
			  validators.Required(message='El email es requerido!'),
			  validators.Email(message='Ingrese un email valido!')
			])

class EliminaUsuario(Form):
	username = SelectField('Usuario', choices = [('1','Oskar'),('2','chesmin'),('3','arti')])

class BuscaServicio(Form):
	servicio = SelectField('Servicio', choices=[('1','FTP'),('2','Correo')])

class EditaServicio(Form):
	name = StringField('nombre',[validators.Required(message='El nombre es requerido!')])
