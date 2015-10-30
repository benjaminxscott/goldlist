#!/usr/bin/env python

from flask import Flask, render_template

app = Flask(__name__)

# ----- DB SETUP -----
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, Listing, Location

engine = create_engine ('sqlite:///listings.db')
Base.metadata.bind = engine

DBsession = sessionmaker(bind = engine)
session = DBsession()

# ----- URL ROUTING -----

@app.route('/')
def landing():
    return render_template("dashboard.html")
    
@app.route('/about')
def about():
    return render_template("about.html")
    
@app.route('/listings')
def show_inventory():

    # list all items in current inventory
    inventory = session.query(Listing).all()
    
    return render_template("listings.html", inventory=inventory)
    

@app.route('/listing/new', methods=['GET','POST'])

def add_inventory():
    # TODO use GET variable "name" and "description" and "location" if provided and generate the rest
    # TODO grab post data for item like ^
    
    #if request.method == 'POST':
     #   item = Listing()
    
    # TODO generate backlink using url_for on location/
    msg = "Good job - added " # TODO popup a toast msg %s" % item.name
    return msg # TODO render_template("dashboard.html", message=msg)
    
@app.route('/listing/edit/<int:listing_id>', methods=['GET','POST'])
def edit_inventory(listing_id):
    # TODO make changes to the given listing
    return "TODO"
    

@app.route('/listing/delete<int:listing_id>', methods=['GET','POST'])
def delete_inventory():
    # TODO remove the given listing
    return "TODO"

@app.route('/location/<int:loc_id>/')
def show_location(loc_id):

    inventory = session.query(Listing).filter_by(loc_id = loc_id) 
    
    return render_template("listings.html", inventory=inventory)



# ----- APP LOGIC -----


# ----- RUN CONFIG ------
if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)