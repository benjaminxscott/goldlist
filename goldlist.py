#!/usr/bin/env python

from flask import Flask, render_template, url_for, request

app = Flask(__name__)

# ----- DB SETUP -----
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Listing, Location

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
    
    if request.method == 'POST':
        
        new_listing = Listing(name= request.form['name'], description = request.form['description'], price = request.form['price']) #TODO location=request.form['location'])
        session.add(new_listing)
        session.commit()

    
    # TODO listing_name, description = "", price = 0.0, location_id = None
    # TODO return render_template("new-item.html", item = listing, created_successfully=created_successfully
    # TODO set need_user_input as appropriate along with created_successfully    
    
    return render_template("new-item.html", need_user_input=True) 
    
@app.route('/listing/edit/<int:listing_id>', methods=['GET','POST'])
def edit_inventory(listing_id):
    # TODO make changes to the given listing
    return "TODO"
    

@app.route('/listing/delete<int:listing_id>', methods=['GET','POST'])
def delete_inventory(listing_id):
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