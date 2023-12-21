"""Flask App for Flask Cafe."""

import os

from flask import (
    Flask, render_template, session, flash, redirect, url_for, g
)
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, City, Cafe, User
from forms import AddEditCafeForm, CSRFProtection, SignupForm, LoginForm
from sqlalchemy.exc import IntegrityError
from utils import get_cities


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_cafe')
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "shhhh")
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)


#######################################
# auth & auth routes


CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


@app.before_request
def add_csrf_only_form():
    """Add a CSRF-only form so that every route can use it."""

    g.csrf_form = CSRFProtection()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


#######################################
# homepage


@app.get("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


#######################################
# user signup/login/logout


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup.
    GET: shows registration form.
    POST: processes registration. If valid, adds user, logs them in, and
    redirects to cafe list. If invalid, re-presents form w/ invalid message.
    """

    do_logout()

    form = SignupForm()

    if form.validate_on_submit():
        new_user = User.register(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            description=form.description.data,
            email=form.email.data,
            password=form.password.data,
            image_url=form.image_url.data or User.image_url.default.arg,
        )
        try:
            db.session.commit()

        except IntegrityError:
            flash('Username already taken.', 'danger')
            return render_template('/auth/signup-form.html', form=form)

        do_login(new_user)
        flash('You are signed up and logged in.')
        return redirect(url_for('cafe_list'))

    else:
        return render_template('/auth/signup-form.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles logging in user.
    GET: shows login form.
    POST: processes login. If valid, logs user in and redirects to cafe list.
    If invalid, re-presents form w/ invalid message.
    """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            form.username.data,
            form.password.data,
        )

        if user:
            do_login(user)
            flash(f'Hello, {user.username}!')
            return redirect(url_for('cafe_list'))

        flash('Invalid credentials.', 'danger')

    return render_template('/auth/login-form.html', form=form)


@app.post('/logout')
def logout():
    """Handles logging out user."""

    if not g.csrf_form.validate_on_submit() or not g.user:
        flash("Access unauthorized", "danger")
        return redirect(url_for('homepage'))

    do_logout()

    flash('You should have successfully logged out.')
    return redirect(url_for('homepage'))


#######################################
# general user routes


@app.get('/profile/<int:user_id>')
def show_profile(user_id):
    """Shows user profile."""

    if not g.user:
        # if not logged in, you shouldn't be able to view a user's profile
        flash('Access unauthorized', 'danger')
        return redirect(url_for('homepage'))

    user = User.query.get_or_404(user_id)

    return render_template('/profile/detail.html', user=user)

# TODO: left off here! Refer to detail.html (right side)




#######################################
# cafes


@app.get('/cafes')
def cafe_list():
    """Return list of all cafes."""

    cafes = Cafe.query.order_by('name').all()

    return render_template(
        'cafe/list.html',
        cafes=cafes,
    )


@app.get('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Show detail for cafe."""

    cafe = Cafe.query.get_or_404(cafe_id)

    return render_template(
        'cafe/detail.html',
        cafe=cafe,
    )


@app.route('/cafes/add', methods=["GET", "POST"])
# Quotations for each method was the ^ bug ^.
def add_new_cafe():
    """GET: show form for adding a cafe. Form accepts:
            name: required
            description: optional
            url: optional, else must be valid URL
            address: required
            city_code: must be drop-down menu of cities in db
            image_url: optional, else must be valid URL

    POST: handles adding new cafe.
    """

    form = AddEditCafeForm()
    form.city_code.choices = get_cities()

    if form.validate_on_submit():
        # data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        # new_cafe = Cafe(**data)
        # ^ old way, need to validate if image_url is empty string instead:
        new_cafe = Cafe(
            name=form.name.data,
            description=form.description.data,
            url=form.url.data,
            address=form.address.data,
            city_code=form.city_code.data,
            image_url=form.image_url.data or Cafe.image_url.default.arg,
        )

        db.session.add(new_cafe)

        try:
            db.session.commit()

        except IntegrityError:
            flash("Could not add cafe to database.")
            return render_template('/cafe/add-form.html', form=form)

        flash(f'{new_cafe.name} added.')
        return redirect(url_for('cafe_detail', cafe_id=new_cafe.id))

    else:
        return render_template('/cafe/add-form.html', form=form)


@app.route('/cafes/<int:cafe_id>/edit', methods=["GET", "POST"])
def edit_cafe(cafe_id):
    """GET: show form for editing cafe. Form fields same as adding new cafe.
    POST: handles editing cafe.
    """

    cafe = Cafe.query.get_or_404(cafe_id)

    form = AddEditCafeForm(obj=cafe)
    form.city_code.choices = get_cities()

    if form.validate_on_submit():
        form.populate_obj(cafe)

        try:
            db.session.commit()

        except IntegrityError:
            flash("Could not save changes.")
            return render_template('/cafe/edit-form.html', form=form, cafe=cafe)

        flash(f'{cafe.name} edited.')
        return redirect(url_for('cafe_detail', cafe_id=cafe_id))

    else:
        return render_template('/cafe/edit-form.html', form=form, cafe=cafe)