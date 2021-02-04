import json
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify,session
from flask_moment import Moment
from models import *
from flask_migrate import Migrate
import requests
import logging
from functools import wraps
from werkzeug.exceptions import HTTPException

from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

app = Flask(__name__)
moment = Moment(app)


app.config.from_object('config')

db.init_app(app)
migrate = Migrate(app,db)

oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id='5PrFVO8YBGSHJbF6XdvYjFyJ2N0VVj3z',
    client_secret='A9SEQvAG_QdnVVnFal00FT7-5MSKZf4z4INPZn6TLeoTmvsL6rJLoVKXWvjer4bv',
    api_base_url='https://sumesh-fsnd.jp.auth0.com',
    access_token_url='https://sumesh-fsnd.jp.auth0.com/oauth/token',
    authorize_url='https://sumesh-fsnd.jp.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


def search_books_api(query):
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q={}'.format(query))
    
    items=json.loads(response.text)['items']
    
    result=[]
    
    for item in items:
        print('#'*100)
      
        author_list=item.get('volumeInfo',{}).get('authors')
        
        authors=''
        if author_list != None:
            for i,author in enumerate(author_list):
                if i>0:
                    authors+=', '
                authors+=author
            
        category_list=item.get('volumeInfo',{}).get('categories')
        categories=''
        
        if category_list != None:
            for i,category in enumerate(category_list):
                if i>0:
                    categories+=', '
                categories+=category
                
        description=item.get('volumeInfo','No description').get('description','No description')
       
        description=description[:100]+'...'
            
        image_link=item.get('volumeInfo',{}).get('imageLinks',{}).get('smallThumbnail')
        
        title=item.get('volumeInfo',{}).get('title')
        id=item.get('id',None)
        print(title,' ',authors,' ',categories)
        print(image_link)
        print(description)
        print('#'*100)
        result.append(Book(id,title,authors,categories,description,image_link))
        
    return result

def get_book_details(id):
    response = requests.get('https://www.googleapis.com/books/v1/volumes/{}'.format(id))
    print('res=',response.text)
    item = json.loads(response.text)
    print('#'*100)
    
    author_list=item.get('volumeInfo',{}).get('authors')
    
    authors=''
    if author_list != None:
        for i,author in enumerate(author_list):
            if i>0:
                authors+=', '
            authors+=author
        
    category_list=item.get('volumeInfo',{}).get('categories')
    categories=''
    
    if category_list != None:
        for i,category in enumerate(category_list):
            if i>0:
                categories+=', '
            categories+=category
            
    description=item.get('volumeInfo','No description').get('description','No description')
    
    description=description[:100]+'...'
        
    image_link=item.get('volumeInfo',{}).get('imageLinks',{}).get('smallThumbnail')
    
    title=item.get('volumeInfo',{}).get('title')
    id=item.get('id',None)
    print(title,' ',authors,' ',categories)
    print(image_link)
    print(description)

    print('#'*100)
    return Book(id,title,authors,categories,description,image_link)
    
    
        
@app.route('/')
def index():
    return render_template('book_search.html')

@app.route('/search')
def search_books():
    query_string=request.args['query_string']
    print(query_string,'-----------------')
    items=search_books_api(query_string)
    return render_template('book_search.html',items=items)


@app.route('/book/<string:id>')
def book_details(id):
    book = Book.query.filter(Book.id==id).one_or_none()
    if book == None:
        book = get_book_details(id)
        db.session.add(book)
        db.session.commit()

    return jsonify(book.format())
        
        
@app.route('/callback')
def callback_handling():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/dashboard')

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='http://localhost:5000/callback')

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    if 'profile' not in session:
      # Redirect to Login page here
      return redirect('/')
    return f(*args, **kwargs)

  return decorated

@app.route('/dashboard')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))