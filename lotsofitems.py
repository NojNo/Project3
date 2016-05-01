# import what you need
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# import from your database setup file the relevant classes
from database_setup import User, Category, latestItem, Base

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
engine = create_engine('sqlite:///category_items_users.db')
Base.metadata.bind = engine

# create a session object in order to have a staging zone
DBSession = sessionmaker(bind=engine)
session = DBSession()


# create dummy User
User1 = User(name="Nojan Nourbakhsh", email="nojan@hotmail.de",
             picture='http://rosenstein-park.de/Images/Baum_28.jpg')

# Items in category: basketball
category1 = Category(user_id=1, category="Basketball Jerseys")

latestItem1 = latestItem(user_id=1, name="Jersey Michael Jordan",
						 description="Chicago Bulls Mitchell & Ness 1985-86\
						 Road Authentic Jersey - Michael Jordan - Mens",
						 price='255.00', category=category1)

latestItem2 = latestItem(user_id=1, name="Jersey Lebron James",
						 description="Cleveland Cavaliers Road Authentic\
						 Jersey - Lebron James - Mens", price='255.00',
						 category=category1)
session.add_all([User1, category1, latestItem1, latestItem2])
session.commit()


# Items in category: football
category2 = Category(user_id=1, category="Football/Soccer Jerseys")

latestItem1 = latestItem(user_id=1, name="National Jersey Germany",
						 description="Germany 2016 Authentic Home Soccer\
						 Jerseys", price='119.00', category=category2)

latestItem2 = latestItem(user_id=1, name="National Jersey Germany Goalkeeper",
						 description="Germany 2016 LS Home Keeper Jersey",
						 price='89.99', category=category2)
session.add_all([category2, latestItem1, latestItem2])
session.commit()


# Items in category: Ice Hockey
category3 = Category(user_id=1, category="Ice Hockey Jerseys")

latestItem1 = latestItem(user_id=1, name="Calgary Flames Jersey",
						 description="Reebok Calgary Flames Men's Premier\
						 Alternate Custom Jersey - Red",
						 price='199.99', category=category3)

latestItem2 = latestItem(user_id=1, name="Anaheim Ducks Jersey",
						 description="Reebok Anaheim Ducks CCM Classic\
						 Anniversary Throwback Jersey - Purple/Turquoise",
						 price='144.99', category=category3)

latestItem3 = latestItem(user_id=1, name="NHL Jersey",
						description="Men's NHL Reebok White 2016 All-Star\
						Premier Jersey", price='134.99', category=category3)
session.add_all([category3, latestItem1, latestItem2, latestItem3])
session.commit()


print "added Items to the Categories!"