import json
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify,session,abort
from flask_moment import Moment
from models import *
from flask_migrate import Migrate
from flask_cors import CORS,cross_origin
import logging
from functools import wraps
from werkzeug.exceptions import HTTPException
from datetime import datetime
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
from helper_methods import *
from forms import ReviewForm
from auth import *
import os

AUTH0_URL='https://sumesh-fsnd.jp.auth0.com/authorize?audience=http://localhost:5000&response_type=token&client_id=5PrFVO8YBGSHJbF6XdvYjFyJ2N0VVj3z&redirect_uri=https://booksnap.herokuapp.com/home'

SECRET_KEY='booksnap'
AUTH0_DOMAIN='https://sumesh-fsnd.jp.auth0.com'
AUTH0_URL='https://sumesh-fsnd.jp.auth0.com/authorize?audience=http://localhost:5000&response_type=token&client_id=5PrFVO8YBGSHJbF6XdvYjFyJ2N0VVj3z&redirect_uri=https://booksnap.herokuapp.com/home'
CLIENT_ID='5PrFVO8YBGSHJbF6XdvYjFyJ2N0VVj3z'
CLIENT_SHARED_SECRET='A9SEQvAG_QdnVVnFal00FT7-5MSKZf4z4INPZn6TLeoTmvsL6rJLoVKXWvjer4bv'
ALGORITHMS=['RS256']
ACCESS_TOKEN_URL='https://sumesh-fsnd.jp.auth0.com/oauth/token'
AUTHORIZE_URL='https://sumesh-fsnd.jp.auth0.com/authorize'
API_AUDIENCE='http://localhost:5000'
USER_ACCESS_TOKEN='eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IngzOThFR1RoWUQyUS1uYzRVRWxOcSJ9.eyJpc3MiOiJodHRwczovL3N1bWVzaC1mc25kLmpwLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDFjMWY0YjM1ZmJlYjAwNmI0NWE1OGEiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjUwMDAiLCJpYXQiOjE2MTI4ODc1NTYsImV4cCI6MTYxMjg5NDc1NiwiYXpwIjoiNVByRlZPOFlCR1NISmJGNlhkdllqRnlKMk4wVlZqM3oiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTp1c2VyX3Jldmlld3MiLCJnZXQ6dXNlcl9yZXZpZXdzIiwicGF0Y2g6dXNlcl9yZXZpZXdzIiwicG9zdDp1c2VyX3Jldmlld3MiXX0.WX-6_A69nL5zU4ryeJAR8Y7YA33eyGs3Fl95TrDl0ffU_1rrrJZwOIyk9Vo3iplQ_f00cImDlraZSfuNHrTBh392CREVMyeb8gc_4NsIkVXEwlZQu9sPdo6y9r4sknQO0Wqo6tqDWK-TkM5zxyvoSfLlYfKgddsE4OOcSQno8sHaTDb2-fUqs6e-8BQYzS58Xf_D4zcXUhlsFxzz5aeUqRFCDxeG0TzWB6l-hR8euu8MDaw_ryZIDfCB1qpYEDVCAElnnXhEK47US_lXry-JCXW_rkuFnbKN-ggCCCWJ5wShQJtLkFt7gTLmZ93NyBpv-hE3x2yTY8IruxYzRAVRUw'
ADMIN_ACCESS_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IngzOThFR1RoWUQyUS1uYzRVRWxOcSJ9.eyJpc3MiOiJodHRwczovL3N1bWVzaC1mc25kLmpwLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDIyYmVmMjNhZTlkNjAwNmNhZjc1OGIiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjUwMDAiLCJpYXQiOjE2MTI4ODk5MzAsImV4cCI6MTYxMjg5NzEzMCwiYXpwIjoiNVByRlZPOFlCR1NISmJGNlhkdllqRnlKMk4wVlZqM3oiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphbGxfcmV2aWV3cyIsImRlbGV0ZTp1c2VyX3Jldmlld3MiLCJnZXQ6YWRtaW4iLCJnZXQ6YWxsX3Jldmlld3MiLCJnZXQ6YWxsX3VzZXJzIiwiZ2V0OnVzZXJfcmV2aWV3cyIsInBhdGNoOnVzZXJfcmV2aWV3cyIsInBvc3Q6dXNlcl9yZXZpZXdzIl19.p9UB_pCZGeqb0LD5Td04N3un3TaJM2tx8n4kZ28EOJtcSz6J9Szm7lptBERbJyM_TwZN2rATsP3RGYV6JXXJfFPTeuL0JNMhBEoe5FCfofqsrNnaeMuuzsUjDMmQS6GQMAS3kAqW-kBtvUkVPWdA072xplslHNn8V0S__TNf9ZQdRelgzhBqedJMVKrkjip952Crcn-T2I6D5rewS0OHtEfKze3EPr75kKRc-st64Ev9l_sS4eTCIA_BUlARez3tlsMnCLNOvha9vfYIuYezrZiZ_MoYOBDSJWvp4adis8d30OdeS8-YFTovjAR51_3lcBReRQGhITqeb5snmqR-jQ"
CALLBACK='https://booksnap.herokuapp.com/callback'

app = Flask(__name__)
moment = Moment(app)

CORS(app, resources={r"*": {"origins": "*"}})
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app,db)

oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id = CLIENT_ID,
    client_secret=CLIENT_SHARED_SECRET,
    api_base_url= AUTH0_DOMAIN,
    access_token_url=ACCESS_TOKEN_URL,
    authorize_url=AUTHORIZE_URL,
    audience=API_AUDIENCE,
    client_kwargs={
        'scope': 'openid profile email',
    },

)
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'profile' not  in session:
                abort(401)
            token = request.cookies.get('token')
            print('token',token)
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
        
@app.route('/')
@app.route('/home')
def home():
    reviews = []
    if session.get('profile'):
        name = session.get('profile')['name']
    else:
        name='Login'
    return render_template('home.html',name=name)

@app.route('/admin/')
@requires_auth(permission='get:admin')
def admin_index(payload):
    return render_template('admin/index.html')


@app.route('/reviews')
@requires_auth(permission='get:user_reviews')
def get_user_reviews(payload):
    reviews = []
    if session.get('profile'):
        name = session.get('profile')['name']
        id = session.get('profile')['user_id'][session.get('profile')['user_id'].index('|')+1:]
        print(id)
        reviews = User.query.filter(User.id==id).first().reviews
    else:
        name='Login'
    return render_template('user_reviews.html',name=name,reviews=reviews)

@app.route('/search')
def search_books():
    query_string=request.args.get('query_string')
    if query_string == '' or query_string == None :
        flash('Please enter the data in the search field')
        items=[]
    else:
        items=search_books_api(query_string)
    if session.get('profile'):
        name = session.get('profile')['name']
    else:
        name='Login'
    print(name)
    
    return render_template('book_search.html',items=items,name=name)


@app.route('/book/<string:id>')
def book_details(id):
    book = Book.query.get(id)
    
    if book is None :
        try:
            book = get_book_details(id)
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            flash('Error fetching the book')
            
            db.session.rollback()
            print('exception: ',e)
            abort(404)
        
    
    if session.get('profile'):
        name = session.get('profile')['name']
    else:
        name='Login'
    if book is None:
        abort(404)
    reviews = book.reviews
    posted=False
    my_review = None
    book_id=None
    if session.get('profile'):
        user_id = session.get('profile')['user_id'][session.get('profile')['user_id'].index('|')+1:]
        user = User.query.filter(User.id==user_id).first()
        
        for review in reviews:
            if user == review.user:
                posted=True
                my_review = review
                
        
    form = ReviewForm()
    if posted:
        form.title.data=my_review.title
        form.review.data=my_review.comment
        form.rating.data=my_review.rating
        book_id = book.id
        print(book_id)
        
    # db.session.close()
    return render_template('book_detail.html',book_id=book_id,my_review=my_review,posted=posted,reviews=reviews,id=id,name=name,title=book.title,author=book.author,category=book.category,image_link=book.image_link,summary=book.summary,form=form)
        
@app.route('/admin/reviews')
@requires_auth(permission='get:all_reviews')
def admin_fetch_all_reviews(payload):
    if session.get('profile'):
        name = session.get('profile')['name']
    else:
        abort(401)
    reviews = Review.query.all()

    return render_template('admin/reviews.html',reviews=reviews)

@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    tk=auth0.authorize_access_token()
    print('resp',tk)
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    
    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    print('uinfo',userinfo)
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    flash('Welcome '+userinfo['name'])
    user_id=(session.get('profile')['user_id'][session.get('profile')['user_id'].index('|')+1:])
    if not User.query.filter(User.id==user_id ).first():
        user = User(id =  user_id ,username=session['profile']['name'])
        user.insert()

    return redirect(AUTH0_URL)


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=CALLBACK)

@app.route('/logout')
@requires_auth()
def logout(payload):
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint
    params = {'returnTo': url_for('home', _external=True), 'client_id': '5PrFVO8YBGSHJbF6XdvYjFyJ2N0VVj3z'}
    flash('Logout Successful')
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))



@app.route('/profile')
@requires_auth()
def dashboard(payload):
    return render_template('profile.html', 
                            ck= request.cookies.get('token'),
                        name = session['profile']['name'],
                        userinfo=session['profile'],
                        userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))


@app.route('/book/reviews/<string:book_id>',methods=['POST'])
@requires_auth()
def post_review(payload,book_id):
    try:
        print('id =',book_id)
        print(request.form['title'])
        review = Review()
        review.title = request.form['title']
        review.comment = request.form['review']
        review.rating = request.form['rating']

        review.created = datetime.today()
        review.edited = datetime.today()
        print(review)
        review.user_id = session.get('profile')['user_id'][session.get('profile')['user_id'].index('|')+1:]
        review.book_id = book_id
    
        db.session.add(review)
        db.session.commit()
        print('success')
    except Exception as e:
        db.session.rollback()
        flash('Error: Review could not be posted')
        print('error',e)
    finally:
        db.session.close()
        
    return redirect(url_for('book_details',id=book_id))

    
@app.route('/books/<string:book_id>/reviews/<int:review_id>',methods=['DELETE'])
@requires_auth()
def delete_review(payload,book_id,review_id):
    try:
        review = Review.query.get(review_id)
        review.delete()

        flash('Delete successful')
    except Exception as e:
        flash('Delete was unsuccessful')
        db.session.rollback()
    finally:
        db.session.close()
        
    return jsonify({'success':True})

@app.route('/admin/reviews/<int:review_id>',methods=['DELETE'])
@requires_auth(permission='delete:all_reviews')
def admin_delete_review(payload,review_id):
    try:
        review = Review.query.get(review_id)
        review.delete()
        flash('Delete successful')
    except Exception as e:
        flash('Error: Delete failed')
        db.session.rollback()
        print('error',e)
    finally:
        db.session.close()
        
    return jsonify({'success':True})

@app.route('/books/<string:book_id>/reviews/<int:review_id>',methods=['POST'])
@requires_auth()
def update_review(payload,book_id,review_id):
    try:
        review = Review.query.get(review_id)
        print(review)
        review.title = request.form['title']
        review.comment = request.form['review']
        review.rating = request.form['rating']
        review.edited = datetime.today()
        review.insert()
        flash('Changes saved successful')
    except Exception as e:
        db.session.rollback()
        flash('Saving changes failed')
        print('error',e)

    finally:
        db.session.close()
    return redirect(url_for('book_details',id=book_id))




@app.route('/admin/reviews',methods=['GET'])
@requires_auth(permission='get:all_reviews')
def admin_fetch_reviews(payload):            
    reviews = Review.query.all()
    return render_template('admin/reviews.html',reviews=reviews)

@app.route('/admin/users',methods=['GET'])
@requires_auth(permission='get:all_users')
def admin_fetch_users(payload):
    users = User.query.all()
    return render_template('admin/users.html',users=users)


@app.errorhandler(404)
def resource_not_found(error):
    return render_template('errors/404.html')

@app.errorhandler(401)
def not_authenticated(auth_error):
        return render_template('errors/401.html')


@app.errorhandler(500)
def not_authenticated(error):
        return render_template('errors/500.html')

