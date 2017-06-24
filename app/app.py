from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth, OAuthException
from static.textAnalyze import getSentiment, sentimentToList, getClassifier, filterActionItems

# from flask_sslify import SSLify

import requests

from logging import Logger
import uuid

app = Flask(__name__)
# sslify = SSLify(app)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

# Put your consumer key and consumer secret into a config file
# and don't check it into github!!
microsoft = oauth.remote_app(
    'microsoft',
    consumer_key='REPLACEME',
    consumer_secret='REPLACEME',
    request_token_params={'scope': 'offline_access Mail.ReadWrite'},
    base_url='https://graph.microsoft.com/v1.0/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
)


@app.route('/')
def index():
    return render_template('hello.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():

    if 'microsoft_token' in session:
        return redirect(url_for('compose'))

    # Generate the guid to only accept initiated logins
    guid = uuid.uuid4()
    session['state'] = guid

    return microsoft.authorize(callback=url_for('authorized', _external=True), state=guid)

@app.route('/logout', methods = ['POST', 'GET'])
def logout():
    session.pop('microsoft_token', None)
    session.pop('state', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = microsoft.authorized_response()

    if response is None:
        return "Access Denied: Reason=%s\nError=%s" % (
            response.get('error'),
            request.get('error_description')
        )

    # Check response for state
    print("Response: " + str(response))
    if str(session['state']) != str(request.args['state']):
        raise Exception('State has been messed with, end authentication')

    # Okay to store this in a local variable, encrypt if it's going to client
    # machine or database. Treat as a password.
    session['microsoft_token'] = (response['access_token'], '')

    return redirect(url_for('compose'))

@app.route('/compose')
def compose():
    return render_template('compose.html')

@app.route('/review', methods=["POST"])
def review():
    recipient = request.form['recipient']
    subject = request.form['subject']
    body = request.form['body']
    action = request.form['action']
    print(action)
    if action == "Review":
        sentences, scores = getSentiment(body)
        sentiment = sentimentToList(sentences, scores, use_nltk=True)
        classifier = getClassifier("static/classifier.pickle")
        actionItems = "\n".join(filterActionItems(classifier, sentences))
        return render_template('compose.html', sentiment=sentiment,
                                               actionItems=actionItems,
                                               recipient=recipient,
                                               subject=subject,
                                               body=body)
    elif action == "Send":
        return "Sent! (Not really you should write some code here)"

    else:
        return render_template('compose.html', subject="Something went wrong...")

# If library is having trouble with refresh, uncomment below and implement refresh handler
# see https://github.com/lepture/flask-oauthlib/issues/160 for instructions on how to do this

# Implements refresh token logic
# @app.route('/refresh', methods=['POST'])
# def refresh():

@microsoft.tokengetter
def get_microsoft_oauth_token():
    return session.get('microsoft_token')

if __name__ == '__main__':
    app.run(debug=True)
