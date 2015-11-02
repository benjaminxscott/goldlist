#!/usr/bin/env python

from flask import Flask, render_template, url_for, request, flash, Markup

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
def get_inventory():

    return render_template("listings.html")
    

@app.route('/listing/new', methods=['GET','POST'])

def add_inventory():
    
    new_listing = None
    
    # Add our item to DB via provided POST vars
    if request.method == 'POST':

        if request.form['name']:
            name = request.form['name']
        if request.form['description']:
            description = request.form['description']
        if request.form['price']:
            price = request.form['price']
            
        if request.form['location_id']:
            # validate location exists, or insert as "unknown"
            location = get_location(request.form['location_id'])
            if location == None:
                location = Location()
                location.name = "Unknown"
                
        new_listing = Listing(name= name, description = description, price = price, location = location )
        session.add(new_listing)
        session.commit()
        
        msg = "%s has been listed" % new_listing.name
        msg += "<a href = "  
        msg += url_for('edit_inventory', listing_id = new_listing.listing_id, _external = True ) 
        msg += " > Edit it here</a>"
        
        # safe for rendering (no xss)    
        msg = Markup(msg)
        flash(msg)
        
    return render_template("new-item.html", item = new_listing ) 
    
@app.route('/listing/edit/<int:listing_id>', methods=['GET','POST'])
def edit_inventory(listing_id):

    changed_listing = get_listing(listing_id)
    
    # Edit the item provided
    if request.method == 'POST':
        changed_listing = get_listing(listing_id)
        
        if request.form['name']:
            changed_listing.name = request.form['name']
        if request.form['description']:
            changed_listing.description = request.form['description']
        if request.form['price']:
            changed_listing.price = request.form['price']
            
        session.add(changed_listing)
        session.commit()
        
        flash ("Your changes to %s have been saved " % changed_listing.name)

    return render_template("edit-item.html", item = changed_listing ) 
    

@app.route('/listing/delete/<int:listing_id>', methods=['GET','POST'])
def delete_inventory(listing_id):
    # remove the provided listing

    toremove_listing = get_listing(listing_id)
    
    # Remove the item provided
    if request.method == 'POST':

        toremove_listing = get_listing(listing_id)

        session.delete(toremove_listing)
        session.commit()
        
        flash ("Your listing for %s has been removed" % toremove_listing.name)
        
    return render_template("delete-item.html", item = toremove_listing ) 
    

@app.route('/location/<int:loc_id>/')
def show_location(loc_id):

    inventory = session.query(Listing).filter_by(loc_id = loc_id) 
    
    return render_template("listings.html", inventory=inventory)



# ----- APP LOGIC -----

def get_location(location_id):
    location = session.query(Location).filter_by(loc_id = location_id).one()
    return location

def get_listing(listing_id):
    listing = session.query(Listing).filter_by(listing_id = listing_id).one()
    return listing

@app.context_processor
def utility_processor():

    def all_locations():
        # list all locations we know about
        locations = session.query(Location).all()
        
        return locations
        
    def all_listings():
        # list all items in current inventory
        inventory = session.query(Listing).all()
        return inventory
        
    return dict(all_locations=all_locations, all_listings=all_listings)    


# ----- RUN CONFIG ------
if __name__ == '__main__':
    app.debug = True
    with open ("app.cfg", "r") as config:
        app.secret_key = config.read()
    app.run(host = '0.0.0.0', port = 8080)