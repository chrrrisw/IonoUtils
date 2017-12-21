import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class Address(Base):
    __tablename__ = 'address'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    street_name = Column(String(250))
    street_number = Column(String(250))
    post_code = Column(String(250), nullable=False)
    person_id = Column(Integer, ForeignKey('person.id'))
    person = relationship(Person)



class WDCDB(object):
    """A database to hold metadata about a local WDC archive."""

    def __init__(self, base, filename, new=False, enable_vacuum=False):
        super(WDCDB, self).__init__()
        self.base = base
        self.filename = filename
        self.new = new
        self.enable_vacuum = enable_vacuum

        self.url = f'sqlite:///{self.filename}'
        self.engine = None
        self.sessionmaker = None
        self.session = None

    @property
    def is_open(self):
        return self.session is not None

    def open(self):
        if self.session is not None:
            raise Exception('database already open')

        dirpath = os.path.dirname(self.filename)

        if self.new and os.path.exists(dirpath) and os.path.exists(self.filename):
            os.remove(self.filename)

        if not os.path.exists(dirpath):
            prev_mask = os.umask(0)
            os.makedirs(dirpath, mode=0o775)
            os.umask(prev_mask)

        self.engine = create_engine(self.url)



# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///sqlalchemy_example.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)




# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Insert a Person in the person table
new_person = Person(name='new person')
session.add(new_person)
session.commit()

# Insert an Address in the address table
new_address = Address(post_code='00000', person=new_person)
session.add(new_address)
session.commit()



# Make a query to find all Persons in the database
session.query(Person).all()
# [<sqlalchemy_declarative.Person object at 0x2ee3a10>]

# Return the first Person from all Persons in the database
person = session.query(Person).first()
# person.name
# u'new person'

# Find all Address whose person field is pointing to the person object
session.query(Address).filter(Address.person == person).all()
# [<sqlalchemy_declarative.Address object at 0x2ee3cd0>]

# Retrieve one Address whose person field is point to the person object
session.query(Address).filter(Address.person == person).one()
# <sqlalchemy_declarative.Address object at 0x2ee3cd0>

address = session.query(Address).filter(Address.person == person).one()
# address.post_code
# u'00000'
