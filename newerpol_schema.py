from sqlalchemy import Column, Date, DateTime, Index, Integer, LargeBinary, Numeric, String, Table, Text, Unicode
from sqlalchemy.dialects.mssql.base import BIT, MONEY
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base

from db import newerpol

Base = declarative_base()
metadata = Base.metadata

t_MumsandDads = Table(
    'MumsandDads', metadata,
    Column('CID', Unicode(8)),
    Column('Login', Unicode(50)),
    Column('PrimaryEmail', Unicode(255)),
    Column('GenderDesc', Unicode(50), nullable=False),
    Column('FirstName', Unicode(255)),
    Column('Surname', Unicode(255)),
    Column('PersonStatus', String(8, u'SQL_Latin1_General_CP1_CI_AS')),
    Column('OCNameTypeName', Unicode(255), nullable=False),
    Column('ID', Integer, nullable=False),
    Column('StudyYear', Integer),
    Column('StudentTypeCode', Unicode(50)),
    Column('LookupName', Unicode(511))
)


t_MumsandDadsChildren = Table(
    'MumsandDadsChildren', metadata,
    Column('ParentID', Integer, nullable=False),
    Column('ChildName', Unicode(511)),
    Column('YearID', Integer, nullable=False)
)


t_MumsandDadsCouples = Table(
    'MumsandDadsCouples', metadata,
    Column('ParentID', Integer, nullable=False),
    Column('CoupleName', Unicode(511)),
    Column('YearID', Integer, nullable=False)
)


t_MumsandDadsParents = Table(
    'MumsandDadsParents', metadata,
    Column('PeopleID', Integer, nullable=False),
    Column('ParentName', Unicode(511)),
    Column('YearID', Integer, nullable=False)
)


t_MumsandDadsSiblings = Table(
    'MumsandDadsSiblings', metadata,
    Column('PeopleID', Integer, nullable=False),
    Column('SiblingName', Unicode(511)),
    Column('YearID', Integer, nullable=False)
)

# print newerpol.query(t_MumsandDads).filter_by(PersonStatus='Current', StudentTypeCode=u'PG', OCNameTypeName=u'Electrical & Electronic Engineering').all() #, t_MumsandDads.StudentTypeCode=='UG', t_MumsandDads.OCNameTypeName=="Electrical & Electronic Engineering") #.all()
    # print instance
# for instance in newerpol.query(t_MumsandDads):
#     print instance
