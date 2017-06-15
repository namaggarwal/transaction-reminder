from flask import Blueprint, render_template, redirect, session, url_for, request, flash, abort, current_app as app
from model import User
from flask_login import login_required, login_user, current_user
from oauth2client import client
from router import bcrypt
import datetime
import httplib2
import json
import utils
from gmail import GMail
from wunderlist import WunderList, Task, List
from transactionScheduler import TransactionScheduler

pages = Blueprint('pages', __name__,template_folder='templates')

#### String Constants ####
INCLUDE_GRANTED_SCOPES = "include_granted_scopes"
ACCESS_TYPE = "access_type"
AUTH_CODE = "code"
GOOGLE_SECRET = "google_secret"
GOOGLE_ID_TOKEN = "id_token"
GOOGLE_EMAIL = "email"
GOOGLE_ACCESS_TOKEN = "access_token"
GOOGLE_REFRESH_TOKEN = "refresh_token"
GOOGLE_TOKEN_EXPIRY = "token_expiry"
GOOGLE_TOKEN_URI = "token_uri"
GOOGLE_REVOKE_URI = "revoke_uri"
WUNDERLIST_STATE = "wl_state"

@pages.route("/")
@login_required
def home():
    app.logger.debug("User "+current_user.email+" logged in")
    lastBackupTime = "Will backup soon"
    if current_user.lastBackupTime:
        lastBackupTime = utils.datetimeToHumanString(current_user.lastBackupTime)
    return render_template("home.html",lastBackupTime=lastBackupTime)

@pages.route("/login")
def login():
    return render_template("login.html")


@pages.route("/login/wunderlist")
@login_required
def wunderListLogin():

    wl = WunderList(app.config["WUNDERLIST_CLIENT_ID"])

    if AUTH_CODE not in request.args:
        authorization_url, state = wl.get_authorize_url(url_for('pages.wunderListLogin', _external=True))
        session[WUNDERLIST_STATE] = state
        return redirect(authorization_url)
    else:
        token = wl.fetch_token(app.config["WUNDERLIST_CLIENT_SECRET"],session[WUNDERLIST_STATE],request.url)
        user = current_user
        user.wunderListToken = token
        user.wunderListAccess = True
        user.save()
        app.logger.debug("User "+user.email+" provided wunderlist access")
        return redirect(url_for('pages.home'))


@pages.route("/login/google")
def googleLogin():
    flow = client.OAuth2WebServerFlow(client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    scope='email',
    redirect_uri=url_for('pages.googleLogin', _external=True))

    flow.params[INCLUDE_GRANTED_SCOPES] = "true"
    flow.params[ACCESS_TYPE] = 'offline'

    if AUTH_CODE not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        session[GOOGLE_SECRET] = bcrypt.generate_password_hash(app.config["FLASK_SECRET_KEY"])
        return redirect(auth_uri)
    else:
        if not bcrypt.check_password_hash(session[GOOGLE_SECRET], app.config["FLASK_SECRET_KEY"]):
            abort(500)
        auth_code = request.args.get(AUTH_CODE)
        credentials = flow.step2_exchange(auth_code)
        credentials = json.loads(credentials.to_json())
        email = credentials[GOOGLE_ID_TOKEN][GOOGLE_EMAIL]
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            user.googleAccessToken  = credentials[GOOGLE_ACCESS_TOKEN]
            user.googleRefreshToken = credentials[GOOGLE_REFRESH_TOKEN]
            user.googleTokenExpiry  = credentials[GOOGLE_TOKEN_EXPIRY]
            user.googleTokenURI     = credentials[GOOGLE_TOKEN_URI]
            user.googleRevokeURI    = credentials[GOOGLE_REVOKE_URI]
            user.googleEmailAccess  = False
            user.save()
        login_user(user)
        app.logger.debug("User "+email+" logged in to google")
        return redirect(url_for('pages.home'))


@pages.route("/login/google/mail")
@login_required
def googleEmailLogin():
    flow = client.OAuth2WebServerFlow(client_id=app.config["GOOGLE_CLIENT_ID"],
    client_secret=app.config["GOOGLE_CLIENT_SECRET"],
    scope='https://www.googleapis.com/auth/gmail.readonly',
    redirect_uri=url_for('pages.googleEmailLogin', _external=True))

    flow.params[INCLUDE_GRANTED_SCOPES] = "true"
    flow.params[ACCESS_TYPE] = 'offline'

    if AUTH_CODE not in request.args:
        app.logger.debug("User "+current_user.email+" trying to provide email access")
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get(AUTH_CODE)
        credentials = flow.step2_exchange(auth_code)
        credentials = json.loads(credentials.to_json())

        user = current_user
        user.googleAccessToken  = credentials[GOOGLE_ACCESS_TOKEN]
        user.googleRefreshToken = credentials[GOOGLE_REFRESH_TOKEN]
        user.googleTokenExpiry  = credentials[GOOGLE_TOKEN_EXPIRY]
        user.googleTokenURI     = credentials[GOOGLE_TOKEN_URI]
        user.googleRevokeURI    = credentials[GOOGLE_REVOKE_URI]
        user.googleEmailAccess = True
        user.save()
        app.logger.debug("User "+user.email+" provided email access")
        return redirect(url_for('pages.home'))


