from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Length, ValidationError

class Tasks(FlaskForm):
    content = StringField("Agregar Tarea", validators=[Length(max=150, message="La tarea no puede tener más de 150 caracteres")])

    def validate_content(self, field):
        if not field.data or field.data.strip() == "":
            raise ValidationError("¡Asegúrese de agregar una tarea!")