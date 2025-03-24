from wtforms import Form
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, IntegerField, PasswordField, SubmitField
from wtforms import validators

class UserForm(Form):
    id = IntegerField('id',
        [validators.number_range(min=1, max=20, message='valor no valido')]
    )
    nombre = StringField('nombre', [
        validators.DataRequired(message='El nombre es requerido'),
        validators.length(min=4, max=50, message='requiere min=4 max=50')
    ])
    
    direccion = StringField('direccion', [
        validators.DataRequired(message='La direccion es requerida')
    ])
    
    telefono = IntegerField('telefono', [
        validators.DataRequired(message='El telefono es requerido'),
    ])

class LoginForm(FlaskForm):
    username = StringField('Usuario', [
        validators.DataRequired(message='El usuario es requerido'),
    ])

    password = PasswordField('Contraseña', [
        validators.DataRequired(message='La contraseña es requerida'),
    ])
    
    submit = SubmitField('Iniciar sesión')
