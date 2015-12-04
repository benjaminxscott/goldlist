#!/usr/bin/env python

from flask import Flask, render_template, url_for, request, flash, Markup, jsonify

from functools import wraps
from flask import session, redirect, abort
import random, string, json, requests

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# ----- APP CONFIG -----

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

CLIENT_SECRET = json.loads(
    open ("client_secrets.json", "r").read())['web']['client_secret']

app.secret_key = CLIENT_SECRET

app.jinja_env.globals['client_id'] = CLIENT_ID 

# ----- DB SETUP -----
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Listing, Location

engine = create_engine ('sqlite:///listings.db')
Base.metadata.bind = engine

buildsession = sessionmaker(bind = engine)
dbsession = buildsession()

# ----- URL ROUTING -----

# landing page
@app.route('/')
@app.route('/listings', alias = True)
def get_inventory():
    # show entire inventory
    
    return render_template("listings.html", inventory = "all")

@app.route('/api/listings')
#  API ENDPOINT
def api_get_inventory():
    # normally would use api.domain.com/v1/operation for this
    inventory = dbsession.query(Listing).all()
    json_data = jsonify(GoldListing = [item.serialize for item in inventory])
    return json_data

@app.route('/login')
def show_login():
    # store CSRF token in session
    session['csrf_token'] = get_csrf_token()
    return render_template("login.html", csrf_token=session['csrf_token'])

@app.route('/logout')
@app.route('/gdisconnect', alias = True)
def do_logout():
    
    # clear user session 
    if session['access_token'] is None:
        flash( "Looks like you're not logged in")
     	abort (401)
    	
    google_api_userlogout = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % session['access_token']
    response = requests.get(google_api_userlogout)

    if response.status_code is not 200:
	    flash( "Looks like you're not logged in")
	    abort (401)
    else:
        # successfully logged the user out
    	del session['access_token']
    	del session['username']
    	del session['email']
    	del session['gplus_id']
    	del session['avatar']
    	del session['provider']
    	flash ("You have been logged out")
    	
    return redirect(url_for("get_inventory"))

@app.route('/gconnect', methods=['POST'])
def do_login():
    
    # Validate CSRF token

    if request.args.get('csrf_token') != session['csrf_token']:
        print "Bad CSRF token"
        abort(401)

    one_time_code = request.data # sent from jquery
    
    # exchange one-time-code for server-side access token
    # (after getting a client secret): https://gist.github.com/bschmoker/74187bad5bbd0a0bf336
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(one_time_code)
    except FlowExchangeError:
        print "Oauth2 one-time-code was bogus" 
        abort(401)
    

    # store credentials for later use
    session['access_token'] = credentials.access_token
    session['gplus_id'] = credentials.id_token['sub']
    session['provider'] = 'google'
    
    
    # lookup user's name and avatar    
    google_api_userinfo = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {
        'access_token': session['access_token'],
        'alt': 'json'
        }
    
    response = requests.get( google_api_userinfo, params=params )
    resp_data = response.json()

    session['username'] = resp_data['name']
    session['avatar'] = resp_data['picture']
    session['email'] = resp_data['email']
    

    # update username on top right profile link
    app.jinja_env.globals['username'] = session['username'] 
    return redirect(url_for("get_inventory"))

@app.route('/listing/new', methods=['GET','POST'])
def add_inventory():
    
    # Check that user is logged in
    if session.get('username') == None:
        return redirect(url_for('show_login'))
    
    new_listing = None
    error = False
    
    # Add our item to DB via provided POST vars
    if request.method == 'POST':

        # validate req'd fields
        if (
            request.form['name'] is not None and 
            request.form['price'] is not None and 
            request.form['location_id'] is not None
            ):
                
            name = request.form['name']
            price = request.form['price']
            
            # validate location exists
            try:
                location = dbsession.query(Location).filter_by(loc_id = request.form['location_id']).one()
            except:
                flash("That doesn't look like a valid location") 
                error = True
                
            # optional fields
            if request.form['description']:
                description = request.form['description']
            else:
                description = ""
            
        if not error:
            # store in DB        
            new_listing = Listing(name= name, description = description, price = price, location = location )
            dbsession.add(new_listing)
            dbsession.commit()
            
            # build a flash message safe for rendering (no xss)    
            msg = "Nice! Would you like to  <a href = "  
            msg += url_for('edit_inventory', listing_id = new_listing.listing_id, _external = True ) 
            msg += " >make any edits to %s? </a>" % new_listing.name
            
            msg = Markup(msg)
            flash(msg)
            
    return render_template("new-item.html", item = new_listing ) 
    
@app.route('/listing/edit/<int:listing_id>', methods=['GET','POST'])
def edit_inventory(listing_id):
    
    # Check that user is logged in
    if session.get('username') == None:
        return redirect(url_for('show_login'))
        
    changed_listing = None
    
    try:
        changed_listing = dbsession.query(Listing).filter_by(listing_id = listing_id).one()
    
    except :
        flash("Looks like that listing doesn't exist")
        
    
    # Edit the item provided
    if request.method == 'POST':
        
        if request.form['name']:
            changed_listing.name = request.form['name']
        if request.form['description']:
            changed_listing.description = request.form['description']
        if request.form['price']:
            changed_listing.price = request.form['price']
            
        dbsession.add(changed_listing)
        dbsession.commit()
        
        flash ("Your changes to %s have been saved " % changed_listing.name)
        
            
    return render_template("edit-item.html", item = changed_listing ) 
    

@app.route('/listing/delete/<int:listing_id>', methods=['GET','POST'])
def delete_inventory(listing_id):
    
    # Check that user is logged in
    if session.get('username') == None:
        return redirect(url_for('show_login'))
    
        
    # remove the provided listing

    if request.method == 'POST':
        try:
            toremove_listing = dbsession.query(Listing).filter_by(listing_id = listing_id).one()
            dbsession.delete(toremove_listing)
            dbsession.commit()
            flash ("Your listing for %s has been removed" % toremove_listing.name)
            
        except:
            flash("Looks like that listing has been removed already")
        
    return render_template("delete-item.html", listing_id=listing_id) 
    

@app.route('/location/<int:loc_id>/')
def show_location(loc_id):

    # filter by this location
    inventory = dbsession.query(Listing).filter_by(loc_id = loc_id) 
    
    if len( inventory.all() ) == 0:
        flash ("Looks like there is nothing listed at that location")
    
    return render_template("listings.html", inventory=inventory)



# ----- UTILITY FUNCTIONS -----


def get_csrf_token():
    token = ''
    for each in xrange(32):
        token += random.choice(string.ascii_uppercase + string.digits) 

    return token


@app.context_processor
def utility_processor():

    def all_locations():
        # list all locations we know about
        locations = dbsession.query(Location).all()
        return locations
        
    def all_listings():
        # list all items in current inventory
        inventory = dbsession.query(Listing).all()
        return inventory
        
    return dict(all_locations=all_locations, all_listings=all_listings)    


# ----- RUN CONFIG ------
if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 8080)