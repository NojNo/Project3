# import relevant modules, class from SQLAlchemy, Flask, my DB-setup,
# the OAUTH Library and from Python

from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Category, Base, latestItem, User


# adding imports that are necessary for Google Sign In
import hashlib
import os
# session is used by SQLAlchemy, thats why Flasks version of session
# needs to be imported
from flask import session as login_session  # login_session as keyword
from oauth2client.client import flow_from_clientsecrets
# creates flow obj from client_secret.json and stores important OAuth2
# parameters
from oauth2client.client import FlowExchangeError
# catches error if an error appears during the exchange of an authorization
# code for access toke
import httplib2
# comprehensive http client library in Python, which is a great helper
# during the dev. of authentication
import json
# JSON helps to convert Python objects into a specific lightweigth
# interchange data format
from flask import make_response
# converts the return value (from function) into real response object
# that we can send to client
import requests
# is an Apache2 library which helps with HTTP requests. It is
# is a DICE library compared to the build in urllib2
# now we can use the JSON file downloaded from the Google Dev.Console

##########################lets start the actual code###########################

# create instance of the class with name of the the running App
# everytime you run the App a special var called name gets definied for the App
# with all the imports it uses
app = Flask(__name__)

# here we declare client_id by referenceing the client_secret.json
CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Category Item Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///category_items_users.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# in here I use different decorators, which wrap functions inside the app.route
# function which is created by Flask
# the function in def will then be executed. This is what the user sees
# basically routing binds function to URL

# before using JSON we need to import jsonify from Flask
# this allows us to easily configure an API endpoint
# here we add JSON APIs to be able to communicate only
# data/information from one App to the other
# now the information about home or a category or
# even an item are publicly available so that external Apps can access them
# because of JSON we also serialized certain information in the DB
# JSON is only used to GET information in this App. We could also
# implement other types of requests
@app.route('/home/JSON')
def homeJSON():
    categories = session.query(Category).all()
    # important: we do not return templates. we return the relevant data
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/home/<int:category_id>/latestitem/JSON')
def showLatestItemJSON(category_id):
    categories = session.query(Category).all()
    latest = session.query(latestItem).filter_by(
        category_id=category_id).all()
    return jsonify(latest=[l.serialize for l in latest])


@app.route('/home/<int:category_id>/latestitem/<int:latestitem_id>/JSON')
def showSINGLELatestItemJSON(category_id, latestitem_id):
    single_latest = session.query(latestItem).filter_by(
        id=latestitem_id).one()
    return jsonify(single_latest=single_latest.serialize)


# Create anti-forgery state token to identify each session
# Create a state token to prevent malicious requests
# store it in state for later validation
@app.route('/login')
def login():
    # Create a unique state token to prevent request forgery.
    # it is a random string
    # Store it in the session for later validation.
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    login_session['state'] = state
    # with the help of render_template we have access to the templates and can
    # also use variables in the templates. Important: templates are saved in
    # the same named folder. You can use HTML escaping as Flask
    # Templates are preconfig.
    # return current session state
    # now the state token is passed into index.html
    return render_template('index.html', STATE=state)


# gooogle connect page, which accepts POST requests in order to send data
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # verifty previously created session token to
    # ensure that the request is not a forgery and that the user sending
    # this connect request is the expected user
    # so compare client to server token to server to client token
    # if no match -> Error message
    # Get a person's profile in OpenID Connect format
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    # if statement is not true, collect one-time code with the help of
    # request.data and store it in code
    code = request.data

    try:
        # try to exchange code variable/one-time code for credentials
        # object which contains acccess token from server
        # Upgrade the authorization code into a credentials object
        # 1. create OAuth Flow
        # 2. add client_secret-key info to it
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        # 3. ensure, that this the one-time code-flow that the server is
        #    sending
        oauth_flow.redirect_uri = 'postmessage'
        # 4. initiate exchange and passing in the one-time code
        #    This answers on the data-redirecturi="postmessage" from
        #    index.html
        credentials = oauth_flow.step2_exchange(code)
        # so if all goes well, Google sends object which will be saved in
        # credentials
        # now we have exchanged authorization code for credentials object
    # else sends error as JSON object
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # now we have credentials object from Google
    # Check that the access token is valid.
    # 1. save access token from credentials in a variable
    access_token = credentials.access_token
    # 2. append token to a the following url in order to receive a
    #    varification from Google
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # 3. create JSON GET request
    #       a) get url + access token
    h = httplib2.Http()
    #       b) store result in a var
    result = json.loads(h.request(url, 'GET')[1])
    # now we should have a working access_token
    # If there was an error in the access token info/result variable
    # send error
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # now we want to ensure, the working access_token is also
    # the right access_token
    # Verify that the access token is used for the intended user.
    # 1. grab id of the token from credentials
    gplus_id = credentials.id_token['sub']
    # 2. compare id from credentials object which origned from Google
    # (the OAuth Provider) to the id from the Google API Server
    # (the Resource Provider)
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # similarly to the access token, we check the client_id
    # Verify that the access token is valid for this APP.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # check to see if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    # if she is, all the loggin settings will not be resetted
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is\
            already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # if none of the if-statements from above turn true,
    # we have a valied access token and the user is successfully logged in
    # to the APP

    # Store the access token in this login_session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # ADD PROVIDER TO LOGIN SESSION in order to enable routing to /disconnect
    login_session['provider'] = 'google'
    # the provider info simplifies the code, if I had multiple OAuth2 provider
    # Get user info by using Google Plus API to get some more information
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    # 1. send message to Google API Server with access token in order
    #    to request the allowed token scope
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    # 2. store information in an object call data
    #    All the stored values that the user has confirmed on the consent
    #    screen can now be accessed with data. This depends on what we
    #    have requested in data-scope
    data = answer.json()

    # store the values that we are interested in loggin-session
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # see if user exists, if she does not make a new one
    user_id = getUserID(data["email"])
    # 1. check if user = none
    if not user_id:
        # 2. if so, we create new user and pass in login_session
        user_id = createUser(login_session)
    # 3. then store user_id in login session under user_id
    login_session['user_id'] = user_id

    # if it works, we know the users name and we can now customize their
    # webexperience
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:\
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Hello %s" % login_session['username'])
    # gives out flashing message that welcomes the user, if he logs in.
    # in order to use flash, you need Flasks version of session
    # sessions help to create a more personalized UX
    print "done!"
    return output


# DISCONNECT - Revoke a current users token and reset their login_session
# disconnects user from google Signin by rejecting the access token
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnects a connected user.
    # 1. grab credentials from login_session and save it
    credentials = login_session.get('credentials')
    # if credentials = empty, you are not connected soo you cannot be
    # disconnected
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # 2. take the access token from the credentials var.
    access_token = credentials.access_token
    # 3. add the access token to the Google URL for revoking tokens
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    # 4. store Googles response in the result object.
    result = h.request(url, 'GET')[0]
    # now we have executed HTTP GET request to revoke current token
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# takes in login_session as input and creates new user in DB with the necessary
# information
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# if user.id is passed in, it returns the right user object
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# if user.email is passed in and we have the user in DB, returns user.id
# we check by email as logging in with different OAUTH provider will return
# the same user
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# helper function to query one category_id
def category_finder(category_id):
    category = session.query(Category).filter_by(id=category_id).one()
    return category


# you can stack decorators on eachother. the first router calls the 2nd
# the 2nd calls the 3rd and so on
@app.route('/')
@app.route('/home/')
@app.route('/home')
def home():
    # grab all categories from the DB
    categories = session.query(Category).order_by(asc(Category.category))
    # if the user is not in the login_session, you will see the public homepage
    if 'username' not in login_session:
        return render_template('publichome.html', find_category=categories)
    else:
        return render_template('home.html', find_category=categories)


# route to the new category page
# Create a new category
# by default - only reacts to GET. by adding the method argument, you
# can add POST requests
# in order to be able to use data from a form, you need to import request
# from flask
@app.route('/home/new', methods=['GET', 'POST'])
def newCategory():
    # if user does a POST request, we create a newCategory and commit it
    # to the DB. After this you will be redirected to the homepage
    # therefore you need to import redirect from flask
    if request.method == 'POST':
        # if the user is the creator of a category, she is the owner.
        # this usertype has many usescases such as edit/delete a category/item
        newCategory = Category(category=request.form['typed_name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        flash('New Category was created. It is called %s' %
              newCategory.category)
        return redirect(url_for('home'))
        # url_for streams the right url. it is basically a hyperlink
        # takes in the url and can take in arguments
        # redirect takes place after your action has been done
    else:
        return render_template('newCategory.html')
        # if there is no POST request, the App will display the
        # newCategory.html template


# route to edit page. Here you can edit the category.
@app.route('/home/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    # returns object which is saved in the var editCategory
    editCategory = category_finder(category_id)
    if editCategory.user_id != login_session['user_id']:
        # if you are not the owner and type in the URL
        # you will see this message:
        return "<script>function myFunction() {alert('You are not authorized to access this page. Please create your own category.');}</script><body onload='myFunction()''>"
    if request.method == "POST":
        if request.form['typed_name']:
            editCategory.category = request.form['typed_name']
            flash('You edited %s successfully. Nice job!'
                  % editCategory.category)
            # now the edited name is saved
            return redirect(url_for('home'))
    else:
        return render_template('editCategory.html', find_category=editCategory)


# route to delete page. Here you can delete a category.
# First you need to find the right one
@app.route('/home/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    deleteCategory = category_finder(category_id)
    if deleteCategory.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to access this page. Please create your own category.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(deleteCategory)
        session.commit()
        flash('You deleted %s successfully. I hope it was the right \
            category haha!' % deleteCategory.category)
        # now the category is deleted
        return redirect(url_for('home'))
    else:
        return render_template('deleteCategory.html',
                               find_category=deleteCategory)


# show all the lastItems per Category
# routes to a page where you can find the latestitem in a category
@app.route('/home/<int:category_id>/')
@app.route('/home/<int:category_id>/latestitem/')
def showLatestItem(category_id):
    showCategory = category_finder(category_id)
    creator = getUserInfo(showCategory.user_id)
    latest = session.query(latestItem).filter_by(
        category_id=category_id).all()
    # if the user is not in the login_session,
    # you will see the public latestitem page
    if ('username' not in login_session or
        creator.id != login_session['user_id']):
        return render_template('publicshowLatestItem.html', find_item=latest,
                               find_category=showCategory, creator=creator)
    else:
        # now you can see the all items in the category
        return render_template('showLatestItem.html', find_item=latest,
                               find_category=showCategory, creator=creator)


# routes to the page where you can add a new item to the category
@app.route('/home/<int:category_id>/latestitem/new/', methods=['GET', 'POST'])
def newLatestItem(category_id):
    showCategory = category_finder(category_id)
    if showCategory.user_id != login_session['user_id']:
        # if you are not the owner and type in the URL,
        # you will see this message:
        return "<script>function myFunction() {alert('You are not authorized to access this page. Please create your own category.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newItem = latestItem(name=request.form['typed_name'],
                             description=request.form['description'],
                             price=request.form['price'],
                             category_id=category_id)
        session.add(newItem)
        session.commit()
        # now a new item is added
        return redirect(url_for('showLatestItem', category_id=category_id))
    else:
        return render_template('newLatestItem.html', find_category=category_id)


# routes to the right item in the right category on the delete page
@app.route('/home/<int:category_id>/latestitem/<int:latestitem_id>/edit/',
           methods=['GET', 'POST'])
def editLatestItem(category_id, latestitem_id):
    showCategory = category_finder(category_id)
    # now we even query the unique ID
    editedItem = session.query(latestItem).filter_by(id=latestitem_id).one()
    if showCategory.user_id != login_session['user_id']:
        # if you are not the owner and type in the URL,
        # you will see this message:
        return "<script>function myFunction() {alert('You are not authorized to access this page. Please create your own category');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['typed_name']:
            editedItem.name = request.form['typed_name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        # now the edited name is saved
        flash('You edited %s successfully. Nice job!' % showCategory.category)
        flash('Now you can find %s in this list' % editedItem.name)
        return redirect(url_for('showLatestItem', category_id=category_id))
    return render_template('editLatestItem.html', find_item=editedItem,
                           find_category=showCategory)


# routes to the right item in the right category on the the delete page
@app.route('/home/<int:category_id>/latestitem/<int:latestitem_id>/delete/',
           methods=['GET', 'POST'])
def deleteLatestItem(category_id, latestitem_id):
    showCategory = category_finder(category_id)
    itemToDelete = session.query(latestItem).filter_by(id=latestitem_id).one()
    if showCategory.user_id != login_session['user_id']:
        # if you are not the owner and type in the URL,
        # you will see this message:
        return "<script>function myFunction() {alert('You are not authorized to access this page. Please create your own category');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('You deleted %s successfully. Nice job!' % itemToDelete.name)
        # now the item is deleted
        return redirect(url_for('showLatestItem', category_id=category_id))
    else:
        return render_template('deleteLatestItem.html', find_item=itemToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    # just selectt the relevant provider
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            # we call the gconnect function
            # then we delete all the relevant information mentioned below
            gdisconnect()
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['picture']
            del login_session['email']
        # successfull log out will be used as an answer
        flash("You have successfully been logged out.")
        return redirect(url_for('home'))
    else:
        flash("Currently not logged in")
        return redirect(url_for('home'))


# if code executed within Python interpreter than do the following else,
# dont do it but at least you have access to rest of the code
# this is great during development
if __name__ == '__main__':
    # here we create a secret key for the sessions of our user
    app.secret_key = 'should_be_super_secret_key_if_live'
    app.debug = True
    # auto-restart server each time we modify the code and provides debugger
    # in the browser
    # this is helpful during development
    app.run(host='0.0.0.0', port=5000)
    # run the local server with our App
    # this is by default for debugging mode
    # as we use VM we have to make changes publicly availablet thats why
    # run contains host and port number
    # 0.0.0.0. means listen to all public IP addresses
