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

AUTH0_URL = os.environ.get('AUTH0_URL')


app = Flask(__name__)
moment = Moment(app)

CORS(app, resources={r"*": {"origins": "*"}})
app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app,db)

oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id = os.environ.get('CLIENT_ID'),
    client_secret=os.environ.get('CLIENT_SHARED_SECRET'),
    api_base_url= os.environ.get('AUTH0_DOMAIN'),
    access_token_url=os.environ.get('ACCESS_TOKEN_URL'),
    authorize_url=os.environ.get('AUTHORIZE_URL'),
    audience=os.environ.get('API_AUDIENCE'),
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
    return auth0.authorize_redirect(redirect_uri=os.environ.get('CALLBACK'))

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

