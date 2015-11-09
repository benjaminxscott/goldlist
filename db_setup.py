#!/usr/bin/env python

# Create a local database given schema

import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# make a skeleton db
Base = declarative_base()


class Location(Base): # extends Base
    __tablename__ = 'location'
    loc_id = Column( Integer, primary_key = True )
    name = Column (String(128) , nullable = False)

class Listing (Base):
    __tablename__ = 'listing'
    listing_id = Column (Integer, primary_key = True)
    name = Column(String(128), nullable = False)
    description = Column(String(256), nullable = True)
    price = Column(Float)
     
    
    loc_id = Column(Integer, ForeignKey('location.loc_id'))
    location = relationship(Location)

    # json definition 
    @property
    def serialize(self):
        return {
            'name':self.name ,
            'listing_id':self.listing_id ,
            'description':self.description ,
            'price':self.price ,
            'location_id':self.loc_id 
            }
            
# spell out where our db will live and its type
engine = create_engine( 'sqlite:///listings.db')

# write tables and columns to disk
Base.metadata.create_all(engine)