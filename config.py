import os
SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SQLALCHEMY_DATABASE_URI = r'postgresql://postgres:password@localhost:5432/booksnap_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
