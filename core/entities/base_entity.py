"""
This module defines the SQLAlchemy base class for declarative class definitions.
The Base class is used as a foundation for creating database models with SQLAlchemy's ORM.

Example usage:

    from sqlalchemy.orm import declarative_base
    
    Base = declarative_base()
    
    class User(Base):
        __tablename__ = 'users'
        
        id = Column(Integer, primary_key=True)
        name = Column(String)

This module should be imported and used in other scripts where SQLAlchemy models are defined.
"""

from sqlalchemy.orm import declarative_base

Base = declarative_base()
