from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from db import *

Base = declarative_base()

class InterestCategory(Base):
	__tablename__ = 'interestcategory'

	id = Column(Integer, primary_key=True)
	CategoryName = Column(String(30))

Base.metadata.create_all(engine)