from wtforms import Form, StringField, TextField, validators, HiddenField, PasswordField
from wtforms.fields.html5 import EmailField

def length_honneypot(form, field):
    if len(field.data)>0:
        raise validators.ValidationError('El campo debe estar vacio.')

class CommentForm(Form):
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
    comment = TextField('Comentario')
    honneypot = HiddenField('',[length_honneypot])

class LoginForm(Form):
    username = StringField('username',
          [
            validators.Required(message='El username es requerido!'),
            validators.length(min=4, max=25, message='Ingrese un username valido!')
          ])
    password = PasswordField('Password',[validators.Required(message='El password es requerido')])
