from flask import Flask, redirect, url_for, session, request, render_template
from flask_oauthlib.client import OAuth
from .helper.textAnalyze import getSentiment, nltkAdjust, getClassifier, filterActionItems
import uuid
import requests
import json

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
    request_token_params={'scope': 'offline_access Mail.ReadWrite Mail.Send'},
    base_url='https://graph.microsoft.com/v1.0/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://login.microsoftonline.com/common/oauth2/v2.0/token',
    authorize_url='https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    content_type='application/json'
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
        return 'Access Denied: Reason=%s\nError=%s' % (
            response.get('error'),
            request.get('error_description')
        )

    # Check response for state
    print('Response: ' + str(response))
    if str(session['state']) != str(request.args['state']):
        raise Exception('State has been messed with, end authentication')

    # Okay to store this in a local variable, encrypt if it's going to client
    # machine or database. Treat as a password.
    session['microsoft_token'] = (response['access_token'], '')

    return redirect(url_for('compose'))

@app.route('/compose')
def compose():
    return render_template('compose.html')

@app.route('/review', methods=['POST'])
def review():
    recipient = request.form['recipient']
    subject = request.form['subject']
    body = request.form['body']

    initialSentiment = getSentiment(body)
    sentiment = nltkAdjust(initialSentiment)
    classifier = getClassifier('app/helper/classifier.pickle')
    results = filterActionItems(classifier, sentiment)
    return render_template('compose.html', results=results,
                                           recipient=recipient,
                                           subject=subject,
                                           body=body,
                                           review=True)


@app.route('/send', methods=['POST'])
def send():
    recipient = request.form['recipient']
    subject = request.form['subject']
    body = request.form['body']

    r = microsoft.post('me/sendMail', content_type="application/json",
                        headers={'content-type': 'application/json'},
                        data=json.dumps({'Message': {
                                            'subject': subject,
                                            'body': {
                                                'contentType': 'text',
                                                'content': body
                                            },
                                            'toRecipients': [{
                                                'emailAddress': {
                                                    'address': recipient
                                                }
                                            }]
                                            },
                                        'SaveToSentItems': 'true'
                                        })
                            )

    if r.status == 202: result = "Success! Insert link back here"
    else: result = "Failed..."
    return result

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
