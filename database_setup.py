# important everything you need from SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# create a table with 4 columns: id, name, email and picture
# this table is important for the LOCAL PERMISSION SYSTEM in order to
# know what data belongs to whom
# This is also the reason why the foreign key user.id is added to the
# other tables
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# create table with 3 columns: id, category and the foreign key for
# user_id
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    category = Column(String(250), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # we serialize because of JSON format. here we diminish which data
    # we will send across and put it an easy readable format
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'category': self.category,
           'id': self.id,
        }


# create table with 6 columns: id, name, description, price and the
# foreign keys for category_id and user_id
class latestItem(Base):
    __tablename__ = 'latest_Item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # we serialize because of JSON format. here we diminish which data
    # we will send across and put it an easy readable format
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'name': self.name,
           'description': self.description,
           'id': self.id,
           'price': self.price,
        }

engine = create_engine('sqlite:///category_items_users.db')


Base.metadata.create_all(engine)