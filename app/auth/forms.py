from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    email = StringField("Correo Electrónico", validators=[DataRequired(message="Por favor introduzca su correo electrónico"), Email(message="Asegúrese de introducir un correo electrónico válido")])
    password = PasswordField("Contraseña", validators=[DataRequired(message="Por favor introduzca su contraseña"), Length(min=8, max=20, message="La contraseña debe tener entre 8 y 20 caracteres")])
    submit = SubmitField("Iniciar Sesión")

class RegistrationForm(FlaskForm):
    name = StringField("Nombre Completo", validators=[DataRequired(message="Por favor introduzca su nombre completo")])
    email = StringField("Correo Electrónico", validators=[DataRequired(message="Por favor introduzca su correo electrónico"), Email(message="Asegúrese de introducir un correo electrónico válido")])
    password = PasswordField("Contraseña", validators=[DataRequired(message="Por favor introduzca su contraseña"), Length(min=8, max=20, message="La contraseña debe tener entre 8 y 20 caracteres")])
    confirm_password = PasswordField("Confirmar Contraseña", validators=[DataRequired(message="Por favor confirme su contraseña"), EqualTo('password', message="Las contraseñas no coinciden")])

class ResetPasswordForm(FlaskForm):
    email = StringField("Correo Electrónico",validators=[DataRequired(message="Por favor introduzca su correo electrónico"), Email(message="Asegúrese de introducir un correo electrónico válido")])

class ResetPasswordTokenForm(FlaskForm):
    password = PasswordField("Nueva Contraseña 🔐", validators=[DataRequired(message="Por favor introduzca su nueva contraseña"), Length(min=8, max=20, message="La contraseña debe tener entre 8 y 20 caracteres")])
    confirm_password = PasswordField("Confirmar Contraseña ✔️", validators=[DataRequired(message="Por favor confirme su nueva contraseña"), EqualTo('password', message="Las contraseñas no coinciden")])