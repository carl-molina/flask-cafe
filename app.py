"""Flask App for Flask Cafe."""

import os

from flask import Flask, render_template, session, flash, redirect, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, City, Cafe
from forms import AddEditCafeForm
from sqlalchemy.exc import IntegrityError
from utils import get_cities


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///flask_cafe')
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "shhhh")
app.config['SQLALCHEMY_ECHO'] = True
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)

#######################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."


# @app.before_request
# def add_user_to_g():
#     """If we're logged in, add curr user to Flask global."""

#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])

#     else:
#         g.user = None


# def do_login(user):
#     """Log in user."""

#     session[CURR_USER_KEY] = user.id


# def do_logout():
#     """Logout user."""

#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]


#######################################
# homepage

@app.get("/")
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


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
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        new_cafe = Cafe(**data)

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