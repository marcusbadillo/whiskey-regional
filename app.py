# flask imports
from flask import Flask, render_template, make_response, request, redirect
from flask import jsonify, url_for, flash, send_from_directory
from flask import session as login_session

# SQLAlchemy imports
from sqlalchemy import create_engine, asc, desc, func, distinct, join, select
from sqlalchemy.orm import sessionmaker

# class / model imports
from create_db import Base, Region, Whiskey, User

# for creating random states -- showLogin()
import random
import string

# client library for accessing resources protected by OAuth 2.0
# https://github.com/google/oauth2client
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# authoriazation login_required decorator
from functools import wraps

# cross-site request forgery - https://flask-seasurf.readthedocs.io/en/latest/
from flask_seasurf import SeaSurf

# HTTP client library -- https://github.com/jcgregorio/httplib2
import httplib2

# Data interchange lib
import json

# Requests allow you to send HTTP/1.1 requests
# https://pypi.python.org/pypi/requests
import requests

# for file uploads
import os
from werkzeug import secure_filename

# list manipulation
from operator import itemgetter


app = Flask(__name__)
# CSRF  https://flask-seasurf.readthedocs.io/en/latest/
csrf = SeaSurf(app)

# upload functionality
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Max up img upload in 16mb
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Whiskey Regions Web App"


# Connect to Database and create database session
engine = create_engine('sqlite:///whiskey_regions.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# login decoration
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function


# upload helper functions / route
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Create anti-forgery state token
@app.route('/login')
def showLogin():

    nologin = "True"
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, nologin=nologin)


# Connect with google Oauth 2.0
@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3 class="text-center">Hello, '
    output += login_session['username']
    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " class="profile-img-card" id="profile-img"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "Logged in!"
    return output


# DB helper functions
def createUser(login_session):

    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):

    user = session.query(User).filter_by(id=user_id).first()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/gdisconnect')
def gdisconnect():

    """ Revoke current user token and reset their login_session """

    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # create dict
    cred = json.loads(credentials)
    access_token = cred["access_token"]
    # add tocken to url
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON API End Points
@app.route('/brands/JSON')
def allBrandsJSON():
    """ Return all brands of whiskey in webapp """

    brands = session.query(Whiskey).all()
    return jsonify(AllBrands=[i.serialize for i in brands])


@app.route('/regions/JSON')
def allRegionsJSON():
    """ Return all regions in webapp """

    regions = session.query(Region).all()
    return jsonify(AllRegions=[i.serialize for i in regions])


@app.route('/brands/<int:id>/JSON')
def singleBrandJSON(id):
    """ Return single brand data """

    whiskey = session.query(Whiskey).filter_by(id=id).all()
    return jsonify(WhiskeyInfo=[i.serialize for i in whiskey])


@app.route('/regions/<int:id>/JSON')
def singleRegionJSON(id):
    """ Return single region data """

    region = session.query(Region).filter_by(id=id).all()
    return jsonify(RegionInfo=[i.serialize for i in region])


# XML API End Points
@app.route('/brands/XML')
def allBrandsXML():
    """ Return all brands of whiskey in webapp """

    brands = session.query(Whiskey).all()
    brands_list = [i.serialize for i in brands]
    xml_all_brands = render_template('all-brands.xml', brands_list=brands_list)
    response = make_response(xml_all_brands)
    response.headers["Content-Type"] = "application/xml"
    return response


@app.route('/regions/XML')
def allRegionsXML():
    """ Return all regions in webapp """

    regions = session.query(Region).all()
    regions_list = [i.serialize for i in regions]
    all_regions = render_template('all-regions.xml', regions_list=regions_list)
    response = make_response(all_regions)
    response.headers["Content-Type"] = "application/xml"
    return response


@app.route('/')
@app.route('/index')
def showApp():

    """
    Returns landing page of app with the top four users with most content
    created and last four whiskies added to database.
    """

    # Lastest Spirts Added
    lastest_whiskey_added = session.query(Whiskey).order_by(
                                          desc(Whiskey.date_added)).limit(4)

    # Top Whiskey Pros
    q = session.query(func.count(Whiskey.user_id), User).filter(
                Whiskey.user_id == User.id).group_by(
                Whiskey.user_id).limit(4)
    sorted_query = sorted(q, key=itemgetter(0), reverse=True)

    return render_template('index.html',
                           lastest_whiskey_added=lastest_whiskey_added,
                           q=sorted_query)


# all Regions
@app.route('/regions')
def showRegions():

    regions = session.query(Region).order_by(asc(Region.name))
    return render_template('regions.html', regions=regions)


# single Region
@app.route('/regions/<string:region>')
def single_region(region):

    # query all brands in this region
    brands_in_region = session.query(Whiskey).filter_by(region=region).all()

    region_query = session.query(Region.name).filter_by(name=region).all()

    name = "null"
    for i in region_query:
        name = i.name

    if(name == region):
        # add a <p> to the brands_in_region list (see view autoescape false)
        for i in brands_in_region:
            user = session.query(User).filter_by(id=i.user_id).one()
            para_el = '<p><span>Created By: %s </span>  <img src="%s"\
            class="img-circle" height="32" width="32"/></p>' % (user.name,
                                                                user.picture)
            i.p = para_el

        return render_template('showRegion.html',
                               brands_query=brands_in_region,
                               region=region)
    else:
        return render_template('404.html')


# all Brands
@app.route('/brands')
def showBrands():

    brands = session.query(Whiskey.name).order_by(asc(Whiskey.name))
    return render_template('brands.html', brands=brands)


# Single Brand
@app.route('/brands/<string:brand>')
def singleBrand(brand):

    # Query for this single brand and get all details
    brand_query = session.query(Whiskey).filter(Whiskey.name == brand).all()

    name = "null"
    for i in brand_query:
        name = i.name

    if(name == brand):

        # find id of user that created this brand
        creator_user_id = session.query(Whiskey.user_id).filter_by(
                                        name=brand).one()

        # query creator of this region
        brand_creator = getUserInfo(creator_user_id[0])

        return render_template('single-brand.html',
                               brand_query=brand_query,
                               brand=brand,
                               creator=brand_creator)
    else:
        return render_template('404.html')


# Add new whiskey
@app.route('/whiskey/new', methods=['GET', 'POST'])
@login_required
def newWhiskey():
    # e == container for errors
    e = ""
    all_regions = session.query(Region).all()
    if request.method == 'GET':

        return render_template('new-whiskey.html',
                               all_regions=all_regions,
                               e=e)
    else:
        # init erros container
        name = request.form['name'].strip()
        description = request.form['description'].strip()
        type = request.form['type'].strip()
        manufac = request.form['manufacturer'].strip()
        abv = request.form['abv'].strip()
        region = request.form.get('region', '')
        file = request.files['file']

        if not name or not description or not type or not manufac or not abv \
           or not region or not file:
            e = "Please enter all the fields."

        if not e:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                newWhiskey = Whiskey(name=request.form['name'],
                                     description=request.form['description'],
                                     img_name=filename,
                                     type=request.form['type'],
                                     manufacturer=request.form['manufacturer'],
                                     abv=request.form['abv'],
                                     region=request.form['region'],
                                     user_id=login_session['user_id'])

                session.add(newWhiskey)
                flash('New Whiskey %s Successfully Added' % newWhiskey.name)
                session.commit()
                return redirect(url_for('showApp'))
        else:
            return render_template("new-whiskey.html",
                                   all_regions=all_regions,
                                   e=e)


# Edit a whiskey
@app.route('/brands/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def editWhiskey(id):

    editedWhiskey = session.query(Whiskey).filter_by(id=id).one()
    all_regions = session.query(Region).all()
    # prepare old img name for  for deletion
    oldimg_name = editedWhiskey.img_name

    if editedWhiskey.user_id != login_session['user_id']:
        flash('You are not authorized to edit %s.' % editedWhiskey.name)
        flash('Please create your own whiskey in order to edit or delete.')
        return redirect(url_for('showApp'))

    if request.method == 'POST':

        # get updated image
        file = request.files['file']

        if request.form['name']:
            editedWhiskey.name = request.form['name']

        if request.form['description']:
            editedWhiskey.description = request.form['description']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # delete old img from database
            os.remove(UPLOAD_FOLDER + '/' + oldimg_name)

            # save new img
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # save new img file name to database
            editedWhiskey.img_name = filename

        if request.form['type']:
            editedWhiskey.type = request.form['type']

        if request.form['manufacturer']:
            editedWhiskey.manufacturer = request.form['manufacturer']

        if request.form['abv']:
            editedWhiskey.abv = request.form['abv']

        if request.form['region']:
            editedWhiskey.region = request.form['region']

        flash('%s successfully edited.' % editedWhiskey.name)
        return redirect(url_for('showApp'))
    else:
        return render_template('edit-whiskey.html', brand=editedWhiskey,
                               all_regions=all_regions)


# Delete a whiskey
@app.route('/brands/<int:id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteWhiskey(id):

    # query whiskey if user is logged
    whiskeyToDelete = session.query(Whiskey).filter_by(id=id).one()

    # check if user is the creator of this whiskey
    if whiskeyToDelete.user_id != login_session['user_id']:
        flash('You are not authorized to delete %s.' % whiskeyToDelete.name)
        flash('Edit and delete whiskeys you have created only.')
        return redirect(url_for('showApp'))

    if request.method == 'POST':
        session.query(Whiskey).filter(Whiskey.id == whiskeyToDelete.id).\
                                      delete(synchronize_session=False)

        # get name of file
        whiskey_img = whiskeyToDelete.img_name

        # delete img from database
        os.remove(UPLOAD_FOLDER + '/' + whiskey_img)

        flash('%s Successfully Deleted' % whiskeyToDelete.name)
        session.commit()
        return redirect(url_for('showApp'))
    else:
        return render_template('delete-whiskey.html', brand=whiskeyToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showApp'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showRegions'))


# 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 500 errors
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 404


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='localhost', port=8000)
