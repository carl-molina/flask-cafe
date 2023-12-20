"""Utils/helper functions for Flask Cafe app."""

from models import City


def get_cities():
    """Get cities for SelectField on forms that add/edit a cafe."""

    cities = [(c.code, c.name) for c in City.query.all()]
    return cities

