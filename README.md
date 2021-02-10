# BookSnap 
## Description
This project consists of a Flask application for browsing and reviewing books (Goodreads/Librarything clone). 
Currently BookSnap is a simple platform, enabling users to post and share book reviews with the community.

The Application consists two types of users: Booksnap User and Booksnap Admin.
Authorization of users is enabled via Auth0 in which two seperate roles (Booksnap User and Booksnap Admin) have been created and assigned seperate permissions.

A user must be authorized as a User to be able to post/edit/delete reviews. 

A user must be authorized as an Admin to access the admin dash https://booksnap.herokuapp.com/admin.


## Project dependencies
The project depends on the latest version of Python 3.x which can be download and install from their official website.
It is recommended to use a virtual environment to install all dependencies.

## PIP dependencies
After having successfully installed Python, navigate to the root folder of the project (the project must be forked to your local machine) and run the following in a command line:
```
pip3 install -r requirements.txt
```
This will install all the required packages to your virtual environment to work with the project.

## Database setup
The models.py file contains connection instructions to the Postgres database, which must also be setup and running. Provide a valid username and password, if applicable.

Create a database with name booksnap_db using Psql CLI:
create database booksnap_db;
Initiate and migrate the database with the following commands in command line:
```
flask db 
flask db migrate 
flask db upgrade 
```
This will create all necessary tables and relationships to work with the project.

## Data Modelling
The data model of the project is provided in models.py file in the root folder. 

The following schema for the database and helper methods are used:
There are four tables created: users , reviews, and books.

- The users table stores the user data aftera successful signup redrect form auth0.
- The reviews table stores the user review information. It has a foreign key on the user table for user_id, and another foreign key on the books table for book_id. 
- The books table is used to sotre the basic book information. A new entry is created when a new book is browsed.

## Helper Methods
The helper methods contains the functions that consume the GoogleBooks API and returns the book data.

## THIRD-PARTY AUTHENTICATION
#### auth.py
Auth0 is set up and running. The configurations are hard coded in the server.
The JWT token contains the permissions for the 'BookSnap User' and 'BookSnap Admin' roles.
The token is stored on the browser as a cookie.

## Application Structure
    @app.errorhandler decorators were used to format error and render appropiate templates. 
    Custom @requires_auth decorator were used for Authorization based on roles of the user. Two roles are assigned to this API: 'BookSnap User' and 'BookSnap Admin'. 
    A token is stored as a cookie after successful login and is sent along with subsequent requests. 
    The token can be retrived by following these steps:
    1. Go to https: https://booksnap.herokuapp.com/
    2. Login successfully
    3. Click on your username on the navbar ( or go to https: https://booksnap.herokuapp.com/)
            OR
        You can just check the browser cookie with key as 'token'

    The following only works for /products endpoints:
    
    2. Click on Login and enter any credentials into the Auth0 login page. The User role needs to be assigned explicitly. 
    A sample account that has already been created can be used:
    Email: test123@gmail.com
    Password: Testing@123
### Jinja2 Templates
    layouts/main.html - Base template with navbar.
    home.html - Booksnap index/home page
    book_search - Displays the book search result list
    book_detail - Diplays the book information along with the reviews. It contains options to post/edit/delete ones review.
    profile - Displays the User information along with the access token.

    admin/index.html - Admin index page
    admin/users.html - Display BookSnap users.
    admin/moderator_reviews.html - Dispaly all reviews with an option to delete reviews.

### URL endpoints

#### GET '/home' 
Renders home.html

#### GET '/reviews'
Fetches user(Self) reviews and renders it on reviews.html

#### GET '/search'
Query parameter: query_string
Uses the helper_methods to search for the query_string from GoogleBooks API, and then renders the list on books_search.hml

#### GET '/book/<string:id>'
Fetches the book data form DB or GoogleBooks API(first search), also fetches the reviews of the given book and displays them on book_details.html

#### GET '/callback'
Callback endpoint to handle auth0 workflow

#### GET '/profile'
Permission/Role - (BookSnap_User)
Fetches user data and access token and dispaly them on profile.html

#### POST '/book/reviews/<string:book_id>'
Permission/Role - (BookSnap_User)
Renders ReviewForm form forms.py and sends a POST to create a review post.
On success, it redirects to book_details.html and flashes success message
else it redirects to one of the errors template


#### DELETE '/book/reviews/<string:book_id>'
Permission/Role - (BookSnap_User)
Sends a delete request to delete the review entry.
A JSON response with success key is returned and a message is flashed

#### POST '/books/<string:book_id>/reviews/<int:review_id>'
Permission/Role - (BookSnap_User)
Renders ReviewForm form forms.py and populates it with exiting data .It sends a POST to create a review post.
On success, it redirects to book_details.html and flashes success message
else it redirects to one of the errors template


#### DELETE '/admin/reviews/<int:review_id>'
Permission/Role - (BookSnap_Admin)
Sends a delete request to delete the review entry.
A JSON response with success key is returned and a message is flashed

#### GET '/admin/'
Permission/Role - (BookSnap_Admin)
Renders admin/index.html

#### GET '/admin/users'
Permission/Role - (BookSnap_Admin)
Renders admin/users.html

#### GET '/admin/reviews'
Permission/Role - (BookSnap_Admin)
Renders admin/reviews.html (with ajax call to delete reviews)


source setup.sh
To run the API server on a local development environmental the following commands must be additionally executed:

On Linux: 
```
export
export FLASK_APP=app.py
export FLASK_ENV=development
```
On Windows: 
```
set
set FLASK_APP=app.py
set FLASK_ENV=development
```

## Flask Server
All accessable endpoints of the project are located in the app.py file.

Run the following command in the project root folder to start the local development server:
flask run

##RBAC credentials and roles
Auth0 was set up to manage role-based access control for two users. The documentation below describes, among others, by which user the endpoints can be accessed. Access credentials and permissions are handled with JWT tockens which are stored on the browser(client side) as cookies.

## Permissions
Users can access endpoints that have the following permission requirements:

'post:user_reviews' - Post a book review
'patch:user_reviews' - Edit a review posted by user(self)
'delete:user_reviews' - Delete a review posted by user (self)
'get:user_reviews' - Fetch all the reviews posted by user(self)

Admins can access endpoints that have the following permission requirements:

'get:all_reviews' - Fetch all the reviews posted by users
'delete:all_reviews' - Delete any review posted by a user
'get:admin' - Fetch the admin dashboard


## Testing
The testing of all endpoints was implemented with unittest. Each endpoint can be tested with one success test case and one error test case. RBAC feature can also be tested for BookSnap user and admin.
Please ensure the constants USER_ACCESS_TOKEN and ADMIN_ACCESS_TOKEN in the test_app.py file are updated with valid tokens.

All test cases are stored in test_app.py file in the project root folder.

Before running the test application, create booksnap_db database using Psql CLI:
Then in the command line interface run the test file:
```
python3 test_app.py
```

## Heroku Deployment and Base URL
The Flask application has been deployed on Heroku and can be accessed at

https://booksnap.herokuapp.com/
