from sqlalchemy import Column, Float, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base, declared_attr

class Base(object):
    """Base class which provides automated table name
    and surrogate primary key column.
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__
    id = Column(Integer, primary_key=True)

    def __repr__(self):
        return str(vars(self))

Base = declarative_base(cls=Base)

class LangleyParticipant(Base):
    node_id = Column(Integer)
    Age = Column(String(100))
    City = Column(String(100))
    Country = Column(String(100))
    Depth_in_Invite_Chain = Column(Float)
    Gender = Column(String(100))
    Number_of_Children = Column(Float)
    Has_Children = Column(Boolean)
    Relationship_with_Parent = Column(String(100))
    Heard_Through_Medium = Column(String(100))
    Has_Parent = Column(Boolean)
    Parent_Child_Registration_Interval = Column(Float)
    Parent_Child_Registration_Interval_Corrected = Column(Float)
    Distance_from_Parent = Column(Float)
    parent_id = Column(Integer)
    Parent_Age = Column(String(100))
    Parent_City = Column(String(100))
    Parent_Country = Column(String(100))
    Parent_Gender = Column(String(100))
    Parent_Number_of_Children = Column(Float)
    Parent_Relationship_with_Grandparent = Column(String(100))
    Parent_Heard_Through_Medium = Column(String(100))
    Grandparent_Parent_Registration_Interval = Column(Float)
    Same_Age_as_Parent = Column(Boolean)
    Same_City_as_Parent = Column(Boolean)
    Same_Country_as_Parent = Column(Boolean)
    Same_Gender_as_Parent = Column(Boolean)
    Same_Relationship_to_Parent_as_They_Had_to_Their_Parent = Column(Boolean)
    Heard_Through_Same_Medium_as_Parent = Column(Boolean)
    Join_Time = Column(DateTime)
    Parent_Join_Time = Column(DateTime)
    Latitude = Column(Float)
    Longitude = Column(Float)

class LangleyDistribution(Base):
    dependent = Column(String(100))
    independent = Column(String(100))
    factor = Column(String(100))
    powerlaw = Column(Integer)
    skew = Column(Float)
    mean = Column(Float)
    median = Column(Float)

class LangleyDistributionCompare(Base):
    dependent = Column(String(100))
    independent = Column(String(100))
    factor1 = Column(String(100))
    factor2 = Column(String(100))
    D = Column(Float)
    KS = Column(Float)
    KW = Column(Float)
    skew = Column(Float)
    median = Column(Float)

#    distribution_id1 = Column(Integer, ForeignKey('LangleyDistribution.id'))
#    distribution_id2 = Column(Integer, ForeignKey('LangleyDistribution.id'))

def create_database(url):
    from sqlalchemy import create_engine

    engine = create_engine(url, echo=False)
    Base.metadata.create_all(engine)
