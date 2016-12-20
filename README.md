# Whiskey Regional - Whiskey By Regions
> A fullstack project built with python, flask (Jinja2 views), PostgreSQL, and Google OAuth 2.0.

## What's inside
In the repo you'll find the following directories and files.

| File/Folder          | Provides                                       |
|----------------------|------------------------------------------------|
| README.md            | how to instructions                            |
| app.py               | Launches app                                   |
| client_secrects.js   | U need to download this file                   |
| create_db.py         | schema SQLAlchemy classes                      |
| load_whiskey.py      | dummy data to insert                           |
| static               | JS, CSS, Fonts, images                         |
| templates            | html views                                     |
| uploads              | directory for user uploads                     |

## Requirements / Dependencies
Local prototyping setup for Mac OS X (10.11.x).
Install python 2 and PostgreSQL however you like.
I like [homebrew](http://brew.sh/) package manager.

1. [python>=2.7.12](https://www.python.org/download/releases/2.7/)
```
[user@machine/~]
$ brew install python
```
2. [PostgreSQL>=9.6.1](https://www.postgresql.org/docs/9.6/static/index.html)
```
[user@machine/~]
$ brew install PostgreSQL
```
3. [flask>=0.11.1](http://flask.pocoo.org/docs/0.11/)
```
[user@machine/~]
$ pip install Flask
```
4. [sqlalchemy>=1.1](http://docs.sqlalchemy.org/en/latest/intro.html)
```
[user@machine/~]
$ pip install SQLAlchemy
```
5. [Flask-SeaSurf>=0.2.2](https://flask-seasurf.readthedocs.io/en/latest/)
```
[user@machine/~]
$ pip install flask-seasurf
```
6. [oauth2client](https://github.com/google/oauth2client)
```
[user@machine/~]
$ pip install --upgrade oauth2client
```
7. [requests](http://docs.python-requests.org/en/master/user/install/)
```
[user@machine/~]
$ pip install requests
```

## Getting Started

1. git clone https://github.com/MediaDUK/whiskey-regional.git
2. enter cloned directory
```
user@machine/~
$ cd /whiskey-regional
```
3. Set up [OAuth 2.0](https://support.google.com/googleapi/answer/6158849?hl=en&ref_topic=7013279).
Python specific implementation [here](https://developers.google.com/api-client-library/python/guide/aaa_oauth)
and download client_secrets.json from  API console after OAuth is enabled and
place in root directory. App cannot insert into local database without user
verification via google account.

4. build database
```
[user@machine ~/whiskey-regional]
$ python create_db.py
```
5. load dummy data
```
[user@machine ~/whiskey-regional]
$ python load_whiskey.py
```
6. run application
```
[user@machine ~/whiskey-regional]
$ python app.py
```
7. open browser to [http://localhost:8000/](http://localhost:8000/)

# JSON & XML Web Services:
Visit the following endpoints to return the specified data

## JSON
##### http://localhost:8000/brands/JSON
Returns all brands

##### http://localhost:8000/regions/JSON
Return all regions

##### http://localhost:8000/brands/<int:id>/JSON
<int:id> == id of brand
Return single brand

##### http://localhost:8000/regions/<int:id>/JSON
<int:id> == id of whiskey
Return single region

## XML
##### http://localhost:8000/brands/XML
Return all brands

##### http://localhost:8000/regions/XML
Return all regions
