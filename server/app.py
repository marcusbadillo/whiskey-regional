import json
import os
import random
import string
from functools import wraps
from operator import itemgetter
from typing import Final, Optional, cast

import httplib2
import requests
from db_models import Base, Region, User, Whiskey
from flask import (
    Flask,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask import session as login_session
from flask_seasurf import SeaSurf
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets
from sqlalchemy import asc, create_engine, desc, func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename

# Absolute path for database file (useful for debugging/logging)
f = os.path.abspath("whiskey_regions.db")

# Create SQLAlchemy engine and create tables if they don't exist
engine = create_engine('sqlite:///whiskey_regions.db')
Base.metadata.create_all(engine)

# Initialize Flask app and CSRF protection via flask-seasurf
app = Flask(__name__)
csrf = SeaSurf(app)

# ------------------------
# Upload configuration
# ------------------------
UPLOAD_FOLDER: Final[str] = "./uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload size

# ------------------------
# Load Google OAuth client ID
# ------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRET_PATH = os.path.join(BASE_DIR, "client_secret.json")

with open(CLIENT_SECRET_PATH, "r") as f:
    CLIENT_ID = json.load(f)["web"]["client_id"]

APPLICATION_NAME: Final[str] = "Whiskey Regions Web App"

# ------------------------
# Database session setup
# ------------------------
engine = create_engine("sqlite:///whiskey_regions.db")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# ------------------------
# Login required decorator
# ------------------------
def login_required(f):
    """
    Decorator to ensure the user is logged in before accessing the route.
    Redirects to login page if not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in login_session:
            return redirect(url_for("showLogin"))
        return f(*args, **kwargs)
    return decorated_function


# ------------------------
# Helper functions for uploads
# ------------------------
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """
    Route to serve uploaded files from the upload folder.
    """
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


def allowed_file(filename: str) -> bool:
    """
    Check if the file has an allowed extension.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------------
# OAuth Login and Logout
# ------------------------
@app.route("/login")
def showLogin():
    """
    Show login page with anti-forgery state token.
    """
    nologin = "True"
    state = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
    login_session["state"] = state
    return render_template("login.html", STATE=state, nologin=nologin)


# Exempt from CSRF because this is a POST from external OAuth provider
@csrf.exempt 
@app.route("/gconnect", methods=["POST"])
def gconnect():
    """
    Google OAuth 2.0 connection handler.
    Exchanges authorization code for credentials,
    validates token info, and stores user info in session.
    """
    # Validate anti-forgery state token
    if request.args.get("state") != login_session.get("state"):
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    code = request.data.decode("utf-8")  # Ensure it’s a str, not bytes


    try:
        oauth_flow = flow_from_clientsecrets(CLIENT_SECRET_PATH,  scope="openid email profile")
        oauth_flow.redirect_uri = "postmessage"
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps("Failed to upgrade the authorization code."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    access_token = getattr(credentials, "access_token", None)
    if not access_token:
        response = make_response(json.dumps("Missing access token."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify access token
    token_info_url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
    h = httplib2.Http()
    result = json.loads(h.request(token_info_url, "GET")[1])

    if result.get("error"):
        response = make_response(json.dumps(result.get("error")), 500)
        response.headers["Content-Type"] = "application/json"
        return response

    id_token = getattr(credentials, "id_token", {})
    gplus_id = id_token.get("sub")
    if not gplus_id:
        response = make_response(json.dumps("Invalid ID token."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    if result["user_id"] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    if result["issued_to"] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    stored_credentials = login_session.get("credentials")
    stored_gplus_id = login_session.get("gplus_id")
    if stored_credentials and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("Current user is already connected."), 200)
        response.headers["Content-Type"] = "application/json"
        return response

    login_session["credentials"] = credentials.to_json()
    login_session["gplus_id"] = gplus_id

    # Retrieve user info from Google API
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {"access_token": access_token, "alt": "json"}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session["username"] = data.get("name")
    login_session["picture"] = data.get("picture")
    login_session["email"] = data.get("email")
    login_session["provider"] = "google"

    # Check if user exists in DB, otherwise create one
    user_id = getUserID(login_session["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session["user_id"] = user_id

    output = f"""
        <h3 class="text-center">Hello, {login_session['username']}!</h3>
        <img src="{login_session['picture']}" class="profile-img-card" id="profile-img">
    """
    flash(f"You are now logged in as {login_session['username']}")
    print("Logged in!")
    return output


@app.route("/gdisconnect")
def gdisconnect():
    """
    Disconnect Google OAuth user by revoking token and clearing session.
    """
    credentials = login_session.get("credentials")
    if credentials is None:
        response = make_response(json.dumps("Current user not connected."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    cred = json.loads(credentials)
    access_token = cred["access_token"]

    url = f"https://accounts.google.com/o/oauth2/revoke?token={access_token}"
    h = httplib2.Http()
    result = h.request(url, "GET")[0]

    if result["status"] != "200":
        response = make_response(json.dumps("Failed to revoke token for given user."), 400)
        response.headers["Content-Type"] = "application/json"
        return response

    response = make_response(json.dumps("Successfully disconnected."), 200)
    response.headers["Content-Type"] = "application/json"
    return response


# ------------------------
# User helper DB functions
# ------------------------
def createUser(login_session) -> int:
    """
    Creates a new user in the database and returns the new user's id.
    """
    new_user = User(
        name=login_session["username"],
        email=login_session["email"],
        picture=login_session["picture"],
    )
    session.add(new_user)
    session.commit()
    return new_user.id


def getUserInfo(user_id: int) -> Optional[User]:
    """
    Retrieves a user object by user ID.
    """
    return session.query(User).filter_by(id=user_id).first()


def getUserID(email: str) -> Optional[int]:
    """
    Retrieves a user ID by email.
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        print(f"user: {user}, type: {type(user)}")
        return user.id
    except NoResultFound:
        return None


# ------------------------
# API Endpoints - JSON and XML
# ------------------------
@app.route("/brands/JSON")
def allBrandsJSON():
    """Return all brands of whiskey as JSON."""
    brands = session.query(Whiskey).all()
    return jsonify(AllBrands=[i.serialize for i in brands])


@app.route("/regions/JSON")
def allRegionsJSON():
    """Return all regions as JSON."""
    regions = session.query(Region).all()
    return jsonify(AllRegions=[i.serialize for i in regions])


@app.route("/brands/<int:id>/JSON")
def singleBrandJSON(id: int):
    """Return single brand data as JSON."""
    whiskey = session.query(Whiskey).filter_by(id=id).all()
    return jsonify(WhiskeyInfo=[i.serialize for i in whiskey])


@app.route("/regions/<int:id>/JSON")
def singleRegionJSON(id: int):
    """Return single region data as JSON."""
    region = session.query(Region).filter_by(id=id).all()
    return jsonify(RegionInfo=[i.serialize for i in region])


@app.route("/brands/XML")
def allBrandsXML():
    """Return all brands of whiskey as XML."""
    brands = session.query(Whiskey).all()
    brands_list = [i.serialize for i in brands]
    xml_all_brands = render_template("all-brands.xml", brands_list=brands_list)
    response = make_response(xml_all_brands)
    response.headers["Content-Type"] = "application/xml"
    return response


@app.route("/regions/XML")
def allRegionsXML():
    """Return all regions as XML."""
    regions = session.query(Region).all()
    regions_list = [i.serialize for i in regions]
    all_regions = render_template("all-regions.xml", regions_list=regions_list)
    response = make_response(all_regions)
    response.headers["Content-Type"] = "application/xml"
    return response


# ------------------------
# Web page routes
# ------------------------
@app.route("/")
@app.route("/index")
def showApp():
    """
    Returns landing page of app with the top users and latest whiskies added.
    """
    lastest_whiskey_added = session.query(Whiskey).order_by(desc(Whiskey.date_added)).limit(4)

    # Query top whiskey creators by count
    q = (
        session.query(func.count(Whiskey.user_id), User)
        .filter(Whiskey.user_id == User.id)
        .group_by(Whiskey.user_id)
        .limit(4)
    )
    sorted_query = sorted(q, key=itemgetter(0), reverse=True)

    return render_template(
        "index.html",
        lastest_whiskey_added=lastest_whiskey_added,
        q=sorted_query,
        flask_token="token",
    )


@app.route("/regions")
def showRegions():
    """
    Display all regions sorted alphabetically.
    """
    regions = session.query(Region).order_by(asc(Region.name))
    return render_template("regions.html", regions=regions)


@app.route("/regions/<string:region>")
def single_region(region: str):
    """
    Show whiskies for a given region name.
    """
    brands_in_region = session.query(Whiskey).filter_by(region=region).all()
    region_query = session.query(Region.name).filter_by(name=region).all()

    name = "null"
    for i in region_query:
        name = i.name

    if name == region:
        # Add HTML snippet to each whiskey for display
        for i in brands_in_region:
            user = session.query(User).filter_by(id=i.user_id).one()
            para_el = (
                '<p><span>Created By: %s </span>  <img src="%s"'
                ' class="img-circle" height="32" width="32"/></p>'
                % (user.name, user.picture)
            )
            i.p = para_el

        return render_template("showRegion.html", brands_query=brands_in_region, region=region)
    else:
        return render_template("404.html")


@app.route("/brands")
def showBrands():
    """
    List all whiskey brand names alphabetically.
    """
    brands = session.query(Whiskey.name).order_by(asc(Whiskey.name))
    return render_template("brands.html", brands=brands)


@app.route("/brands/<string:brand>")
def singleBrand(brand: str):
    """
    Show details for a single whiskey brand by name.
    """
    brand_query = session.query(Whiskey).filter(Whiskey.name == brand).all()

    name = "null"
    for i in brand_query:
        name = i.name

    if name == brand:
        creator_user_id = session.query(Whiskey.user_id).filter_by(name=brand).one()
        brand_creator = getUserInfo(creator_user_id[0])

        return render_template(
            "single-brand.html",
            brand_query=brand_query,
            brand=brand,
            creator=brand_creator,
        )
    else:
        return render_template("404.html")


# ------------------------
# Whiskey CRUD routes
# ------------------------

@app.route("/whiskey/new", methods=["GET", "POST"])
@login_required
def newWhiskey():
    """
    Create a new whiskey entry.
    """
    e = ""
    all_regions = session.query(Region).all()

    if request.method == "GET":
        return render_template("new-whiskey.html", all_regions=all_regions, e=e)

    # POST request processing
    name = request.form["name"].strip()
    description = request.form["description"].strip()
    type = request.form["type"].strip()
    manufac = request.form["manufacturer"].strip()
    abv = request.form["abv"].strip()
    region = request.form.get("region", "")
    file = request.files.get("file")

    if (
        not name
        or not description
        or not type
        or not manufac
        or not abv
        or not region
        or not file
        or not file.filename
    ):
        e = "Please enter all the fields."
        return render_template("new-whiskey.html", all_regions=all_regions, e=e)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        newWhiskey = Whiskey(
            name=name,
            description=description,
            img_name=filename,
            type=type,
            manufacturer=manufac,
            abv=abv,
            region=region,
            user_id=login_session["user_id"],
        )
        session.add(newWhiskey)
        session.commit()
        flash(f"New Whiskey {newWhiskey.name} Successfully Added")
        return redirect(url_for("showApp"))
    else:
        e = "Invalid or missing file."
        return render_template("new-whiskey.html", all_regions=all_regions, e=e)


@app.route("/brands/<int:id>/edit", methods=["GET", "POST"])
@login_required
def editWhiskey(id: int):
    """
    Edit an existing whiskey entry by ID.
    Only the creator can edit.
    """
    editedWhiskey = session.query(Whiskey).filter_by(id=id).one()
    all_regions = session.query(Region).all()
    oldimg_name = editedWhiskey.img_name

    if editedWhiskey.user_id != login_session["user_id"]:
        flash("You are not authorized to edit %s." % editedWhiskey.name)
        flash("Please create your own whiskey in order to edit or delete.")
        return redirect(url_for("showApp"))

    if request.method == "POST":
        file = request.files.get("file")
        filename: Optional[str] = file.filename if file else None
        regionId = request.form["region"]

        if request.form["name"]:
            editedWhiskey.name = request.form["name"]

        if request.form["description"]:
            editedWhiskey.description = request.form["description"]

        if file and filename and allowed_file(filename):
            safe_filename = secure_filename(filename)

            if oldimg_name:
                try:
                    os.remove(os.path.join(UPLOAD_FOLDER, oldimg_name))
                except FileNotFoundError:
                    print(f"Old image {oldimg_name} not found for deletion.")

            file.save(os.path.join(app.config["UPLOAD_FOLDER"], safe_filename))
            editedWhiskey.img_name = safe_filename

        if request.form["type"]:
            editedWhiskey.type = request.form["type"]

        if request.form["manufacturer"]:
            editedWhiskey.manufacturer = request.form["manufacturer"]

        if request.form["abv"]:
            editedWhiskey.abv = request.form["abv"]

        if request.form["region"]:
            region_obj = session.query(Region).filter_by(id=int(regionId)).one_or_none()
            if region_obj:
                editedWhiskey.region = region_obj

        flash(f"{editedWhiskey.name} successfully edited.")
        session.commit()
        return redirect(url_for("showApp"))

    else:
        return render_template("edit-whiskey.html", brand=editedWhiskey, all_regions=all_regions)


@app.route("/brands/<int:id>/delete/", methods=["GET", "POST"])
@login_required
def deleteWhiskey(id: int):
    """
    Delete a whiskey entry by ID.
    Only the creator can delete.
    """
    whiskeyToDelete = session.query(Whiskey).filter_by(id=id).one()

    if whiskeyToDelete.user_id != login_session["user_id"]:
        flash(f"You are not authorized to delete {whiskeyToDelete.name}.")
        flash("Edit and delete whiskeys you have created only.")
        return redirect(url_for("showApp"))

    if request.method == "POST":
        session.query(Whiskey).filter(Whiskey.id == whiskeyToDelete.id).delete(synchronize_session=False)
        whiskey_img = cast(str, whiskeyToDelete.img_name)

        try:
            os.remove(os.path.join(UPLOAD_FOLDER, whiskey_img))
        except FileNotFoundError:
            print(f"Image {whiskey_img} not found for deletion.")

        session.commit()
        flash(f"{whiskeyToDelete.name} Successfully Deleted")
        return redirect(url_for("showApp"))

    else:
        return render_template("delete-whiskey.html", brand=whiskeyToDelete)


# ------------------------
# Disconnect and error handlers
# ------------------------
@app.route("/disconnect")
def disconnect():
    """
    Log out user and clear session based on login provider.
    """
    if "provider" in login_session:
        if login_session["provider"] == "google":
            gdisconnect()
            del login_session["gplus_id"]
            del login_session["credentials"]
        del login_session["username"]
        del login_session["email"]
        del login_session["picture"]
        del login_session["user_id"]
        del login_session["provider"]
        flash("You have successfully been logged out.")
        return redirect(url_for("showApp"))
    else:
        flash("You were not logged in")
        return redirect(url_for("showRegions"))


@app.errorhandler(404)
def handle_404(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def handle_500(e):
    return render_template("500.html"), 500


# ------------------------
# Main app run
# ------------------------
if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host="localhost", use_reloader=True, port=8000, threaded=True)