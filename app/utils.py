import datetime
from oauth2client import client


def getColumnNameFromIndex(index):

    quo = index/26
    rem = index%26

    pre = ""
    post = ""

    if quo != 0:
        pre = chr(quo+64)

    post = chr(rem+65)

    return pre+post


def stringToDatetime(text):

    return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")

def datetimeToString(date):

    return date.strftime("%Y-%m-%dT%H:%M:%SZ")

def datetimeToHumanString(date):

    return date.strftime("%d %B %Y %I:%M:%S %p")


def getGoogleCredentials(app, user):

    tokenExpiry = stringToDatetime(user.googleTokenExpiry)

    googlecredentials = client.GoogleCredentials(
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        access_token=user.googleAccessToken,
        refresh_token=user.googleRefreshToken,
        token_expiry=tokenExpiry,
        token_uri=user.googleTokenURI,
        revoke_uri=user.googleRevokeURI,
        user_agent=None
    )

    return googlecredentials
