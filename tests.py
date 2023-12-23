"""Tests for Flask Cafe."""


import os

os.environ["DATABASE_URL"] = "postgresql:///flaskcafe_test"

import re
from unittest import TestCase

from flask import session
from app import app, CURR_USER_KEY
from models import db, Cafe, City, connect_db, User, Like
from sqlalchemy.exc import IntegrityError

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()


#######################################
# helper functions for tests


def debug_html(response, label="DEBUGGING"):  # pragma: no cover
    """Prints HTML response; useful for debugging tests."""

    print("\n\n\n", "*********", label, "\n")
    print(response.data.decode('utf8'))
    print("\n\n")


def login_for_test(client, user_id):
    """Log in this user."""

    with client.session_transaction() as sess:
        sess[CURR_USER_KEY] = user_id


#######################################
# data to use for test objects / testing forms


CITY_DATA = dict(
    code="sf",
    name="San Francisco",
    state="CA"
)

CAFE_DATA = dict(
    name="Test Cafe",
    description="Test description",
    url="http://testcafe.com/",
    address="500 Sansome St",
    city_code="sf",
    image_url="http://testcafeimg.com/"
)

CAFE_DATA_EDIT = dict(
    name="new-name",
    description="new-description",
    url="http://new-image.com/",
    address="500 Sansome St",
    city_code="sf",
    image_url="http://new-image.com/"
)

CAFE_DATA_NEW = dict(
    name="New Cafe 2",
    description="Test description 2",
    url="http://testcafe.com/",
    address="500 New St",
    city_code="sf",
    image_url="http://testcafeimg.com/"
)

TEST_USER_DATA = dict(
    username="test",
    first_name="Testy",
    last_name="MacTest",
    description="Test Description.",
    email="test@test.com",
    password="secret",
)

TEST_USER_DATA_EDIT = dict(
    first_name="new-fn",
    last_name="new-ln",
    description="new-description",
    email="new-email@test.com",
    image_url="http://new-image.com",
)

TEST_USER_DATA_NEW = dict(
    username="new-username",
    first_name="new-fn",
    last_name="new-ln",
    description="new-description",
    password="secret",
    email="new-email@test.com",
    image_url="http://new-image.com",
)

# ADMIN_USER_DATA = dict(
#     username="admin",
#     first_name="Addie",
#     last_name="MacAdmin",
#     description="Admin Description.",
#     email="admin@test.com",
#     password="secret",
#     admin=True,
# )


#######################################
# homepage


class HomepageViewsTestCase(TestCase):
    """Tests about homepage."""

    def test_homepage(self):
        with app.test_client() as client:
            resp = client.get("/")
            self.assertIn(b'Where Coffee Dreams Come True', resp.data)


#######################################
# cities


class CityModelTestCase(TestCase):
    """Tests for City Model."""

    def setUp(self):
        """Before all tests, add sample city & users."""

        Cafe.query.delete()
        City.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.city_code = sf.code
        self.cafe = cafe

    def tearDown(self):
        """After each test, remove all cafes."""

        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    # depending on how you solve exercise, you may have things to test on
    # the City model, so here's a good place to put that stuff.

    def test_city_sf(self):
        """Tests for City Model on sf city instance."""

        city = City.query.get_or_404(self.city_code)

        self.assertEqual('sf', city.code)
        self.assertEqual('San Francisco', city.name)
        self.assertEqual('CA', city.state)


#######################################
# cafes


class CafeModelTestCase(TestCase):
    """Tests for Cafe Model."""

    def setUp(self):
        """Before all tests, add sample city & users"""

        Cafe.query.delete()
        City.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.cafe = cafe

    def tearDown(self):
        """After each test, remove all cafes."""

        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    def test_get_city_state(self):
        self.assertEqual(self.cafe.get_city_state(), "San Francisco, CA")


class CafeViewsTestCase(TestCase):
    """Tests for views on cafes."""

    def setUp(self):
        """Before all tests, add sample city & users"""

        Cafe.query.delete()
        City.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.cafe_id = cafe.id

    def tearDown(self):
        """After each test, remove all cafes."""

        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    def test_list(self):
        """Tests for cafe listings."""

        with app.test_client() as client:
            resp = client.get("/cafes")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Test Cafe", resp.data)

    def test_detail(self):
        """Tests for cafe profile/detail."""

        with app.test_client() as client:
            resp = client.get(f"/cafes/{self.cafe_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Test Cafe", resp.data)
            self.assertIn(b'testcafe.com', resp.data)


class CafeAdminViewsTestCase(TestCase):
    """Tests for add/edit views on cafes."""

    def setUp(self):
        """Before each test, add sample city, users, and cafes"""

        City.query.delete()
        Cafe.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.cafe_id = cafe.id

    def tearDown(self):
        """After each test, delete the cities."""

        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    def test_add(self):
        """Tests to check adding new cafe."""
        with app.test_client() as client:
            resp = client.get(f"/cafes/add")

            self.assertIn(b'Add Cafe', resp.data)

            resp = client.post(
                f"/cafes/add",
                data=CAFE_DATA_EDIT,
                follow_redirects=True)

            self.assertIn(b'added', resp.data)
            self.assertEqual(resp.status_code, 200)

    def test_add_form_get_cities(self):
        """Tests to check proper cities are in SelectField in add/edit form."""

        with app.test_client() as client:
            resp = client.get("/cafes/add", follow_redirects=True)

            self.assertIn(b'San Francisco', resp.data)

    # a neat regex way to test for the drop-down menu in SelectField!
    def test_dynamic_cities_vocab(self):
        id = self.cafe_id

        # the following is a regular expression for the HTML for the drop-down
        # menu pattern we want to check for
        choices_pattern = re.compile(
           r'<select [^>]*name="city_code"[^>]*><option [^>]*value="sf">' +
           r'San Francisco</option></select>')

        with app.test_client() as client:
            resp = client.get(f"/cafes/add")
            self.assertRegex(resp.data.decode('utf8'), choices_pattern)

            resp = client.get(f"/cafes/{id}/edit")
            self.assertRegex(resp.data.decode('utf8'), choices_pattern)

    def test_edit(self):
        id = self.cafe_id

        with app.test_client() as client:
            resp = client.get(f"/cafes/{id}/edit", follow_redirects=True)
            self.assertIn(b'Edit Test Cafe', resp.data)

            resp = client.post(
                f"/cafes/{id}/edit",
                data=CAFE_DATA_EDIT,
                follow_redirects=True)
            self.assertIn(b'edited', resp.data)

    def test_edit_form_shows_curr_data(self):
        id = self.cafe_id

        with app.test_client() as client:
            resp = client.get(f"/cafes/{id}/edit", follow_redirects=True)
            self.assertIn(b'Test description', resp.data)

    def test_edit_form_get_cities(self):
        """Tests to check proper cities are in SelectField in add/edit form."""
        id = self.cafe_id

        with app.test_client() as client:
            resp = client.get(f"/cafes/{id}/edit", follow_redirects=True)

            self.assertIn(b'San Francisco', resp.data)




#######################################
# users


class UserModelTestCase(TestCase):
    """Tests for User Model."""

    def setUp(self):
        """Before each test, add sample users."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)
        # db.session.add(user)
        # ^ Don't need this! Already does db.session.add(user) in class method!

        db.session.commit()

        self.user = user

    def tearDown(self):
        """After each test, remove all users."""

        User.query.delete()
        db.session.commit()

    def test_authenticate(self):
        rez = User.authenticate("test", "secret")
        self.assertEqual(rez, self.user)

    def test_authenticate_fail(self):
        rez = User.authenticate("no-such-user", "secret")
        self.assertFalse(rez)

        rez = User.authenticate("test", "password")
        self.assertFalse(rez)

    def test_full_name(self):
        self.assertEqual(self.user.full_name, "Testy MacTest")

    def test_register(self):
        u = User.register(**TEST_USER_DATA)
        # test that password gets bcrypt-hashed (all start w/$2b$)
        self.assertEqual(u.hashed_password[:4], "$2b$")
        db.session.rollback()


class AuthViewsTestCase(TestCase):
    """Tests for views on logging in/logging out/registration."""

    def setUp(self):
        """Before each test, add sample users."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)
        # db.session.add(user)
        # ^ don't have this here! The register class method already adds
        # the new user to the database within the fn. This was the bug!!

        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """After each test, remove all users."""

        db.session.rollback()
        # ^ use db.session.rollback() when you force PendingRollbackErrors
        # like when trying to create a new user when that username already
        # exists in the db.

        User.query.delete()
        db.session.commit()

    def test_signup(self):
        """Tests for successful user signup."""

        with app.test_client() as client:
            resp = client.get("/signup")
            self.assertIn(b'Sign Up', resp.data)

            resp = client.post(
                "/signup",
                data=TEST_USER_DATA_NEW,
                follow_redirects=True,
            )

            self.assertIn(b"You are signed up and logged in.", resp.data)
            self.assertTrue(session.get(CURR_USER_KEY))

    def test_signup_username_taken(self):
        """Tests for invalid signup (username already taken)."""

        with app.test_client() as client:
            resp = client.get("/signup")
            self.assertIn(b'Sign Up', resp.data)

            # signup with same data as the already-added user
            resp = client.post(
                "/signup",
                data=TEST_USER_DATA,
                follow_redirects=True,
            )

            self.assertIn(b"Username already taken", resp.data)

    def test_login(self):
        """Tests for user login."""

        with app.test_client() as client:
            resp = client.get("/login")
            self.assertIn(b'Welcome Back!', resp.data)

            resp = client.post(
                "/login",
                data={"username": "test", "password": "WRONG"},
                follow_redirects=True,
            )

            self.assertIn(b"Invalid credentials", resp.data)

            resp = client.post(
                "/login",
                data={"username": "test", "password": "secret"},
                follow_redirects=True,
            )

            self.assertIn(b"Hello, test", resp.data)
            self.assertEqual(session.get(CURR_USER_KEY), self.user_id)

    def test_logout(self):
        """Tests for user logout."""

        with app.test_client() as client:
            login_for_test(client, self.user_id)
            resp = client.post("/logout", follow_redirects=True)

            self.assertIn(b"successfully logged out", resp.data)
            self.assertEqual(session.get(CURR_USER_KEY), None)


class NavBarTestCase(TestCase):
    """Tests navigation bar."""

    def setUp(self):
        """Before tests, add sample user."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)

        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """After tests, remove all users."""

        db.session.rollback()

        User.query.delete()
        db.session.commit()

    def test_anon_navbar(self):
        """Tests view of navbar when user not logged in."""

        with app.test_client() as client:
            resp = client.get('/')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Sign Up', resp.data)
            self.assertIn(b'Log In', resp.data)
            self.assertNotIn(b'Log Out', resp.data)

        with app.test_client() as client:
            resp = client.get('/cafes')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Sign Up', resp.data)
            self.assertIn(b'Log In', resp.data)
            self.assertNotIn(b'Log Out', resp.data)

    def test_logged_in_navbar(self):
        """Tests view of navbar when user logged in."""

        with app.test_client() as client:
            login_for_test(client, self.user_id)
            resp = client.get('/')

            user = User.query.get_or_404(self.user_id)

            self.assertIn(b'Log Out', resp.data)
            self.assertIn(f'{user.full_name}', str(resp.data))
            self.assertNotIn(b'Sign Up', resp.data)
            self.assertNotIn(b'Log In', resp.data)

        with app.test_client() as client:
            login_for_test(client, self.user_id)
            resp = client.get('/cafes')

            user = User.query.get_or_404(self.user_id)

            self.assertIn(b'Log Out', resp.data)
            self.assertIn(f'{user.full_name}', str(resp.data))
            self.assertNotIn(b'Sign Up', resp.data)
            self.assertNotIn(b'Log In', resp.data)


class ProfileViewsTestCase(TestCase):
    """Tests for views on user profiles."""

    def setUp(self):
        """Before each test, add sample user."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)

        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """After each test, remove all users."""

        User.query.delete()
        db.session.commit()

    def test_anon_profile(self):
        """Tests for a non-logged in user trying to enter profile detail."""

        with app.test_client() as client:
            resp = client.get('/profile', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'You are not logged in', resp.data)
            self.assertIn(b'Login', resp.data)

    def test_logged_in_profile(self):
        """Tests for logged in user trying to enter profile detail."""

        with app.test_client() as client:
            login_for_test(client, self.user_id)

            resp = client.get('/profile')

            user = User.query.get_or_404(self.user_id)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(user.full_name, str(resp.data))


    def test_anon_profile_edit(self):
        """Tests for non-logged in user trying to edit profile."""

        with app.test_client() as client:
            resp = client.get('/profile/edit', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'You are not logged in', resp.data)
            self.assertIn(b'Login', resp.data)

            resp = client.post(
                '/profile/edit',
                data=TEST_USER_DATA_EDIT,
                follow_redirects=True,
            )

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'You are not logged in', resp.data)
            self.assertIn(b'Login', resp.data)

    def test_logged_in_profile_edit(self):
        """Tests for logged-in user trying to edit profile."""

        with app.test_client() as client:
            login_for_test(client, self.user_id)

            resp = client.get('/profile/edit')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Edit Profile', resp.data)
            self.assertIn(b'Testy', resp.data)

            resp = client.post(
                '/profile/edit',
                data=TEST_USER_DATA_EDIT,
                follow_redirects=True,
            )

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Profile edited.', resp.data)
            self.assertIn(b'new-fn', resp.data)
            self.assertIn(b'new-description', resp.data)


# #######################################
# likes


class LikeModelTestCase(TestCase):
    """Tests for Like Model."""

    def setUp(self):
        """Before each test, add sample user, city, and cafe for likes."""

        User.query.delete()
        Cafe.query.delete()
        City.query.delete()

        user1 = User.register(**TEST_USER_DATA)
        city = City(**CITY_DATA)
        cafe = Cafe(**CAFE_DATA)

        db.session.add_all([city, cafe])
        db.session.commit()

        self.user1_id = user1.id
        self.city_code = city.code
        self.cafe_id = cafe.id

        like = Like(user_id=self.user1_id, cafe_id=self.cafe_id)

        db.session.add(like)
        db.session.commit()

    def tearDown(self):
        """After each test, remove liked_cafes and delete users and cafes."""

        db.session.rollback()

        user = User.query.get_or_404(self.user1_id)
        # cafe = Cafe.query.get_or_404(self.cafe_id)
        # city = City.query.get_or_404(self.city_code)

        user.liked_cafes.clear()

        User.query.delete()
        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    def test_duplicate_like(self):
        """Tests whether a user already likes a cafe."""

        with self.assertRaises(IntegrityError):
            like = Like(user_id=self.user1_id, cafe_id=self.cafe_id)
            db.session.add(like)
            db.session.commit()


class LikeViewsTestCase(TestCase):
    """Tests for views on cafes."""

    def setUp(self):
        """Before each test, add sample user and sample cafe for likes."""

        User.query.delete()
        Cafe.query.delete()
        City.query.delete()

        user1 = User.register(**TEST_USER_DATA)
        user2 = User.register(**TEST_USER_DATA_NEW)
        city = City(**CITY_DATA)
        cafe = Cafe(**CAFE_DATA)
        cafe2 = Cafe(**CAFE_DATA_NEW)

        db.session.add_all([city, cafe, cafe2])
        db.session.commit()

        self.user1_id = user1.id
        self.user2_id = user2.id
        self.city_code = city.code
        self.cafe_id = cafe.id
        self.cafe2_id = cafe2.id

        user1.liked_cafes.append(cafe)

    def tearDown(self):
        """After each test, remove liked_cafes and delete users and cafes."""

        db.session.rollback()

        user = User.query.get_or_404(self.user1_id)
        # cafe = Cafe.query.get_or_404(self.cafe_id)
        # city = City.query.get_or_404(self.city_code)

        user.liked_cafes.clear()

        User.query.delete()
        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    def test_likes_on_profile(self):
        """Tests for a user having a liked cafe on their profile page."""

        with app.test_client() as client:
            login_for_test(client, self.user1_id)

            resp = client.get('/profile')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'You like Test Cafe', resp.data)
            self.assertNotIn(b'You have no liked cafes!', resp.data)

    def test_no_likes_on_profile(self):
        """Tests for a user having no liked cafes on their profile page."""

        with app.test_client() as client:
            login_for_test(client, self.user2_id)

            resp = client.get('/profile')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'You have no liked cafes!', resp.data)
            self.assertNotIn(b'You like ', resp.data)

    def test_anon_api_likes(self):
        """Tests for non-logged in user when using IIFE processLikes."""

        with app.test_client() as client:
            resp = client.get(f'/api/likes?cafe_id={self.cafe2_id}')

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {"error": "Not logged in"})

    def test_logged_in_api_likes(self):
        """Tests for logged in user when using IIFE processLikes."""

        with app.test_client() as client:
            login_for_test(client, self.user1_id)

            resp = client.get(f'/api/likes?cafe_id={self.cafe2_id}')

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {"likes": False})

    def test_anon_handle_like(self):
        """Tests for non-logged in user liking a cafe."""

        with app.test_client() as client:
            resp = client.post(
                '/api/like',
                json={
                    "cafe_id": self.cafe2_id
                }
            )

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {"error": "Not logged in"})

    def test_user_handle_like(self):
        """Tests for logged-in user liking a cafe."""

        with app.test_client() as client:
            login_for_test(client, self.user1_id)

            resp = client.post(
                '/api/like',
                json={
                    "cafe_id": self.cafe2_id
                }
            )

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {"liked": self.cafe2_id})

    def test_anon_handle_unlike(self):
        """Tests for non-logged in user unliking a cafe."""

        with app.test_client() as client:
            resp = client.post(
                '/api/unlike',
                json={
                    "cafe_id": self.cafe_id
                }
            )

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {"error": "Not logged in"})

    def test_user_handle_unlike(self):
        """Tests for logged-in user liking a cafe."""

        with app.test_client() as client:
            login_for_test(client, self.user1_id)

            resp = client.post(
                '/api/unlike',
                json={
                    "cafe_id": self.cafe_id
                }
            )

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json, {"unliked": self.cafe_id})