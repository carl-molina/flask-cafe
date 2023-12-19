"""Initial data."""

from models import City, Cafe, db  # , User

from app import app

db.drop_all()
db.create_all()


#######################################
# add cities

sf = City(code='sf', name='San Francisco', state='CA')
berk = City(code='berk', name='Berkeley', state='CA')
oak = City(code='oak', name='Oakland', state='CA')

db.session.add_all([sf, berk, oak])
db.session.commit()


#######################################
# add cafes

c1 = Cafe(
    name="Bernie's Cafe",
    description='Serving locals in Noe Valley. A great place to sit and write'
        ' and write Rithm exercises.',
    address="3966 24th St",
    city_code='sf',
    url='https://www.yelp.com/biz/bernies-san-francisco',
    image_url='https://s3-media4.fl.yelpcdn.com/bphoto/bVCa2JefOCqxQsM6yWrC-A/o.jpg'
)

c2 = Cafe(
    name='Perch Coffee',
    description='Hip and sleek place to get cardamom lattés when biking'
        ' around Oakland.',
    address='440 Grand Ave',
    city_code='oak',
    url='https://perchoffee.com',
    image_url='https://s3-media4.fl.yelpcdn.com/bphoto/0vhzcgkzIUIEPIyL2rF_YQ/o.jpg',
)

db.session.add_all([c1, c2])
db.session.commit()


#######################################
# add users

# ua = User.register(
#     username="admin",
#     first_name="Addie",
#     last_name="MacAdmin",
#     description="I am the very model of the modern model administrator.",
#     email="admin@test.com",
#     password="secret",
#     admin=True,
# )

# u1 = User.register(
#     username="test",
#     first_name="Testy",
#     last_name="MacTest",
#     description="I am the ultimate representative user.",
#     email="test@test.com",
#     password="secret",
# )

# db.session.add_all([u1])
# db.session.commit()


#######################################
# add likes

# u1.liked_cafes.append(c1)
# u1.liked_cafes.append(c2)
# ua.liked_cafes.append(c1)

# db.session.commit()


#######################################
# cafe maps

# c1.save_map()
# c2.save_map()
#
#db.session.commit()
