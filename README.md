# Whiskey Regional - Whiskey By Regions

> A fullstack project built with python, flask (Jinja2 views), PostgreSQL, and Google OAuth 2.0.

## What's inside

In the repo you'll find the following directories and files.

| File/Folder                | Provides                               |
| -------------------------- | -------------------------------------- |
| README.md                  | how to instructions                    |
| /client                    | react front end                        |
| /server/app.py             | launch app                             |
| /server/client_secrects.js | see set up OAuth 2.0 (create your own) |
| /server/create_db.py       | schema SQLAlchemy classes              |
| /server/load_whiskey.py    | dummy data to insert                   |
| /server/templates          | html views                             |
| /server/uploads            | directory for user uploads             |

## Requirements / Dependencies

1. install [homebrew](https://brew.sh/) and install the rest with it. Or do you.

2. install [pipenv](https://github.com/pypa/pipenv)

3. install [virtualenv](https://virtualenv.pypa.io/en/stable/installation.html)

4. install [python>=3.7.7](https://www.python.org/)

5. install [PostgreSQL>=12.2](https://www.postgresql.org/)

### Install [flask>=0.11.1](http://flask.pocoo.org/docs/0.11/), [sqlalchemy>=1.1](http://docs.sqlalchemy.org/en/latest/intro.html), [Flask-SeaSurf>=0.2.2](https://flask-seasurf.readthedocs.io/en/latest/), [oauth2client](https://github.com/google/oauth2client), [requests](http://docs.python-requests.org/en/master/user/install/)

```bash
pipenv install
```

> [pipenv review](https://pipenv-fork.readthedocs.io/en/latest/basics.html)

## Getting Started

### Clone & enter repo

```bash
git clone https://github.com/MediaDUK/whiskey-regional.git && cd _$
```

### Enter Virtual Env

```bash
virtualenv [your-env]
source [your-env]/bin/activate
[your-env]/bin/pip install flask sqlalchemy flask_seasurf oauth2client sqlalchemy flask_sqlalchemy requests
```

### Set up [google-api-python-client](https://cloud.google.com/docs/authentication/api-keys)

Once OAuth is enabled download client_secrets.json from API console after and
place in root directory. App cannot insert into local database without user
authentication via google account.

### Build Database, Load Whisky, start app, and open browser to [http://localhost:8000/](http://localhost:8000/)

```bash
pipenv run python create_db.py && python load_whiskey.py && python app.py
```

## Viewing App

### Click top right "Sign In" Button

sign in via google account(email password not implemented yet)--you will be redirected to home page and '+ Whiskey' button
will be available after user verification.

## JSON & XML Web Services

Visit the following endpoints to return the specified data

## JSON

### [http://localhost:8000/brands/JSON](http://localhost:8000/brands/JSON)

> _return all brands_

### [http://localhost:8000/regions/JSON](http://localhost:8000/regions/JSON)

> _return all regions_

### [http://localhost:8000/brands/<int:id>/JSON](http://localhost:8000/brands/<int:id>/JSON)

> _return single brand_

#### [http://localhost:8000/regions/<int:id>/JSON](http://localhost:8000/regions/<int:id>/JSON)

> _return single region_

## XML (eh, why not?)

### [http://localhost:8000/brands/XML](http://localhost:8000/brands/XML)

> _return all brands_

### [http://localhost:8000/regions/XML](http://localhost:8000/regions/XML)

> _return all regions_

<!-- # Whiskey Regional App

This is a Flask-based API server for managing whiskeys by region. A React frontend will be added later.

## Requirements

- Python 3.11+
- pipenv
- Flask

## Setup

```bash
pipenv install
pipenv shell
python app.py -->

{% comment %}
function signInCallback(authResult) {
    if (authResult["code"]) {
      // Hide the sign-in button now that the user is authorized
      $("#signIn-google").attr("style", "display: none");
      $("#signIn-Facebook").attr("style", "display: none");
      $("#login-card").fadeOut("fast");
      // Send the one-time-use code to the server, if server responds,
      // 'login successful' message to the web page and redirect to landing page
      $("#result").html(
        '<h3 class="text-center">Searching!</h3><p class="lead text-center">Just a few seocnds...</p>'
      );
      $("#result").fadeIn("fast");

      $.ajax({
        type: "POST",
        url: "/gconnect?state={{STATE}}",
        processData: false,
        data: authResult["code"],
        contentType: "application/octet-stream; charset=utf-8",
        success: function (result) {
          if (result) {
            console.log(result);

            $("#result").fadeOut("fast");
            $("#result").html(
              '<p class="lead text-center">Login Successful! </p>' +
                result +
                '<p class="lead text-center">Redirecting...</p>'
            );
            $("#result").fadeIn("fast");
            setTimeout(function () {
              window.location.href = "/";
            }, 4000);
          } else if (authResult["error"]) {
            console.log("There was an error: " + authResult["error"]);
          } else {
            $("#result").html(
              "<p>Failed to make a server-side call. Check your configuration and console.</p>"
            );
          }
        },
      });
    }
  } {% endcomment %}
