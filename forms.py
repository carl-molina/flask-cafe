"""Forms for Flask Cafe."""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, PasswordField
from wtforms.validators import InputRequired, URL, Optional, Email, Length


class AddEditCafeForm(FlaskForm):
    """Form for adding/editing a cafe."""

    name = StringField(
        "Name",
        validators=[InputRequired(), Length(max=30)]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )

    url = StringField(
        "URL",
        validators=[Optional(), URL(), Length(max=255)]
    )

    address = StringField(
        "Address",
        validators=[InputRequired(), Length(max=50)]
    )

    city_code = SelectField(
        "City Code"
    )

    image_url = StringField(
        "image_url",
        validators=[Optional(), URL(), Length(max=255)]
    )


class SignupForm(FlaskForm):
    """Form for registering/adding new user."""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(max=30)]
    )

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=30)]
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(max=30)]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )

    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=50)]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6, max=50)]
    )

    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL(), Length(max=255)]
    )


class ProfileEditForm(FlaskForm):
    """Form for editing user profile."""

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(max=30)]
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(max=30)]
    )

    description = TextAreaField(
        "Description",
        validators=[Optional()]
    )

    email = StringField(
        "Email",
        validators=[InputRequired(), Email(), Length(max=50)]
    )

    image_url = StringField(
        "Image URL",
        validators=[Optional(), URL(), Length(max=255)]
    )


class LoginForm(FlaskForm):
    """Login form; takes in username and password."""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(max=30)]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(max=50)]
    )

class CSRFProtection(FlaskForm):
    """CSRFProtection form, intentionally has no fields."""