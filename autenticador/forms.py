from wtforms import Form, StringField, TextField, validators, HiddenField, PasswordField, SelectField
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

	first_name = TextField('Nombre',
                      [
						  validators.Required(message = 'El nombre es requerido'),
						  validators.length(min=2, max=50, message='Ingrese un nombre valido')
					  ])

	last_name = TextField('Apellido',
                        [
  						  validators.Required(message = 'El apellido es requerido'),
  						  validators.length(min=3, max=50, message='Ingrese un apellido valido')
  					  ])


	def validate_username (form, field):
		username = field.data
		user = User.query.filter_by(username = username).first()
		if user is not None:
			raise validators.ValidationError('El username ya se encuentra registrado.')

class CreateServiceForm(Form):
    name = StringField('name',[
	    validators.Required(message='El nombre es requerido!'),
		validators.length(min=3, max=25, message='Ingrese un nombre valido!')
	], default="FTP")


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
	username = SelectField('Usuario', choices=[('Oscar','Oscar'),('Yesme', 'Yesme')])
	rolNuevo= SelectField('Roles', choices=[('1','ADMINISTRADOR'),('2','USUARIO')])
