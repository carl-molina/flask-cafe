"""Data models for Flask Cafe"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from mapping import save_map

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_PROFILE_IMG = '/static/images/default-pic.png'
DEFAULT_CAFE_IMG = '/static/images/default-cafe.jpg'


class City(db.Model):
    """Cities for cafes."""

    __tablename__ = 'cities'

    code = db.Column(
        db.Text,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    state = db.Column(
        db.String(2),
        nullable=False,
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} code={self.code} name={self.name}>"


class Cafe(db.Model):
    """Cafe information."""

    __tablename__ = 'cafes'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    url = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    city_code = db.Column(
        db.Text,
        db.ForeignKey('cities.code'),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default=DEFAULT_CAFE_IMG,
    )

    city = db.relationship("City", backref='cafes')

    def get_city_state(self):
        """Returns 'city, state' for cafe."""

        city = self.city
        return f'{city.name}, {city.state}'

    def save_map(self):
        """Saves map jpg file for location of cafe."""

        city = self.city
        save_map(self.id, self.address, city.name, city.state)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id} name={self.name}>"


class User(db.Model):
    """User information."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.String(30),
        nullable=False,
        unique=True,
    )

    admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    email = db.Column(
        db.String(50),
        nullable=False,
    )

    first_name = db.Column(
        db.String(30),
        nullable=False,
    )

    last_name = db.Column(
        db.String(30),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
        default="",
    )

    image_url =  db.Column(
        db.String(255),
        nullable=False,
        default=DEFAULT_PROFILE_IMG,
    )

    # must pass in hashed_password when creating user instance, not plaintext pw
    hashed_password = db.Column(
        db.String(255),
        nullable=False,
    )

    @property
    def full_name(self):
        """Return a string of 'first_name last_name'."""

        return f'{self.first_name} {self.last_name}'

    @classmethod
    def register(
        cls,
        username,
        first_name,
        last_name,
        email,
        password,
        admin=False,
        description='',
        image_url=DEFAULT_PROFILE_IMG):
        """Register a new user and handle password hashing."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        new_user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            description=description,
            email=email,
            hashed_password=hashed_pwd,
            admin=admin,
            image_url=image_url
        )

        db.session.add(new_user)
        return new_user

    @classmethod
    def authenticate(cls, username, password):
        """Checks db for user w/ correct username and password.

        If found matching user, returns that user object. If not found or if
        password is incorrect, returns False.
        """

        user = cls.query.filter_by(username=username).one_or_none()

        if user:
            is_auth = bcrypt.check_password_hash(user.hashed_password, password)
            if is_auth:
                return user

        return False

    liked_cafes = db.relationship(
        "Cafe", secondary="likes", backref="liking_users"
    )

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id} name={self.username}>"


class Like(db.Model):
    """Tracks which user likes which cafe."""

    __tablename__ = "likes"

    __table_args__ = (
        db.UniqueConstraint("user_id", "cafe_id"),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        primary_key=True,
    )

    cafe_id = db.Column(
        db.Integer,
        db.ForeignKey('cafes.id'),
        primary_key=True,
    )

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} " +
            f"user={self.user_id} cafe={self.cafe_id}>"
        )


def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)