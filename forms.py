"""Forms for Flask Cafe."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import InputRequired, URL, Optional

class AddEditCafeForm(FlaskForm):
    """Form for adding/editing a cafe."""

    name = StringField(
        "Name",
        validators=[InputRequired()]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )

    url = StringField(
        "URL",
        validators=[Optional(), URL()]
    )

    address = StringField(
        "Address",
        validators=[InputRequired()]
    )

    city_code = SelectField(
        "City Code"
    )

    image_url = StringField(
        "image_url",
        validators=[Optional(), URL()]
    )