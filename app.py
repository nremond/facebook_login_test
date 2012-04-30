import os
from flask import Flask, redirect, url_for, session, request, render_template
from flaskext.oauth import OAuth


SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = os.environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.environ.get('FACEBOOK_APP_SECRET')


app = Flask(__name__, static_folder='static', template_folder='templates')
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

facebook = oauth.remote_app('facebook',
	base_url='https://graph.facebook.com/',
	request_token_url=None,
	access_token_url='/oauth/access_token',
	authorize_url='https://www.facebook.com/dialog/oauth',
	consumer_key=FACEBOOK_APP_ID,
	consumer_secret=FACEBOOK_APP_SECRET,
	request_token_params={'scope': 'email'}
)

def authenticated(func):
	def with_logging(*args, **kwargs):
		print func.__name__ + " was called"
		if not get_facebook_oauth_token():
			return redirect(url_for('login'))
		return func(*args, **kwargs)
	return with_logging


@app.route('/')
@authenticated
def index():
	return render_template('index.html', title="nicolas")


@app.route('/login')
def login():
	return facebook.authorize(callback=url_for('facebook_authorized',
		next=request.args.get('next') or request.referrer or None,
		_external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
	if resp is None:
		return 'Access denied: reason=%s error=%s' % (
			request.args['error_reason'],
			request.args['error_description']
		)

	#flash("resp="+resp)
	app.logger.debug("resp="+str(resp))
	
	session['oauth_token'] = (resp['access_token'], '')
	me = facebook.get('/me')
	return 'Logged in as id=%s name=%s redirect=%s' % \
		(me.data['id'], me.data['name'], request.args.get('next'))


@facebook.tokengetter
def get_facebook_oauth_token():
	if 'oauth_token' in session:
		return session['oauth_token']
	else : 
		return None

@app.route('/hello')
def hello():
	return "hello dude"






if __name__ == '__main__':
	# Bind to PORT if defined, otherwise default to 5000.
	port = int(os.environ.get('PORT', 5000))
	use_debugger = False
	app.run(use_debugger=use_debugger, debug=app.debug,
            use_reloader=use_debugger,host='0.0.0.0', port=port)
