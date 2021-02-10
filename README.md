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

##Database setup
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

## Running the local development server
All necessary credential to run the project are provided in the setup.sh file. The credentials can be enabled by running the following command:

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
