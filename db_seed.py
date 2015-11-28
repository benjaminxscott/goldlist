from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, Listing, Location

engine = create_engine('sqlite:///listings.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

pawn = Location(name="Pawn Stars") 

store = Location(name="Storage Wars") 

session.add(pawn)
session.add(store)

session.commit()

# -----
listings = []

listings.append( Listing (location = store, name = "Gold Glasses", description = "worn by the man himself", price = 92) )

listings.append( Listing (location = pawn, name = 'Lock of Hair', price = 18) )

listings.append( Listing (location = pawn, name = "Samuel L Jackson's arm", description = "An arm found lying on the ground next to a raptor cage", price = 18) )

for item in listings:
    session.add(item)

session.commit()