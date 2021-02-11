import os
import unittest
import json
from time import sleep
from app import *
from models import *
from flask import template_rendered
from contextlib import contextmanager
from unittest.mock import patch

USER_PROFILE_DATA={   'user_id': 'auth0|601c1f4b35fbeb006b45a58a',
                        'name': "test123@gmail.com",   }
USER_JWT_PAYLOAD={'sub': 'auth0|601c1f4b35fbeb006b45a58a', 'nickname': 'test123', 'name': 'test123@gmail.com', 'picture': 'https://s.gravatar.com/avatar/9a93efa79aa9f5d35e14bc55a3e16dc4?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fte.png', 'updated_at': '2021-02-08T18:01:30.452Z', 'email': 'test123@gmail.com', 'email_verified': False}
USER_ACCESS_TOKEN = os.environ.get('USER_ACCESS_TOKEN')

ADMIN_PROFILE_DATA={   'user_id': 'auth0|6022bef23ae9d6006caf758b',
                        'name': "admin@booksnap.com",   }
ADMIN_JWT_PAYLOAD = {
    "email": "admin@booksnap.com",
    "email_verified": False,
    "name": "admin@booksnap.com",
    "nickname": "admin",
    "picture": "https://s.gravatar.com/avatar/04524577b0c5a85e2a035b5a4a364ee1?s=480&r=pg&d=https%3A%2F%2Fcdn.auth0.com%2Favatars%2Fad.png",
    "sub": "auth0|6022bef23ae9d6006caf758b",
    "updated_at": "2021-02-09T16:57:22.685Z"
}
USER_ACCESS_TOKEN = os.environ.get('ADMIN_ACCESS_TOKEN')


@contextmanager
def captured_templates(app):
    recorded = []
    def record(sender, template, context, **extra):
        recorded.append((template, context))
    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)

class BookSnapTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
   

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = app
        self.client = self.app.test_client
        self.database_name = "booksnap_db"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','password','localhost:5432', self.database_name)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['TESTING'] = True
     
    def tearDown(self):
        """Executed after each test"""
        print("teardown")


    def test_valid_home(self):
        response = self.client().get('/home')
        self.assertEqual(response.status_code,200)
 
    def test_invalid_unauthenticated_profile(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                r = c.get('/profile')
                template, context = templates[0]
                # self.assertEquals(context['foo'], 'bar')
                self.assertEquals(template.name, 'errors/401.html')
                print(template,context)

    def test_valid_user_profile(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                    with c.session_transaction() as s:
                        s['profile'] = USER_PROFILE_DATA
                        s['jwt_payload'] = USER_JWT_PAYLOAD
                    c.set_cookie('localhost','token',USER_ACCESS_TOKEN)
                    r = c.get('/profile')
                    template, context = templates[0]
                    print(template,context)
                    self.assertEqual(template.name, 'profile.html')

    def test_invalid_unauthenticated_user_reviews(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                r = c.get('/reviews')
                template, context = templates[0]
                self.assertEquals(template.name, 'errors/401.html')
                print(template,context)

    def test_valid_authenticated_user_reviews(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                    with c.session_transaction() as s:
                       s['profile'] = USER_PROFILE_DATA
                       s['jwt_payload'] = USER_JWT_PAYLOAD
                    c.set_cookie('localhost','token',USER_ACCESS_TOKEN)
                    r = c.get('/reviews')
                    template, context = templates[0]
                    print(template,context)
                    self.assertEqual(template.name, 'user_reviews.html') 

   
    def test_valid_search(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                r = c.get('/search?query_string=Steppenwolf')
                template, context = templates[0]
                self.assertEquals(len(context['items']), 10)
                self.assertEqual(template.name, 'book_search.html')
                print(template,context)
        
    def test_valid_book_detail(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                r = c.get('/book/X7YmCwAAQBAJ')
                template, context = templates[0]
                self.assertEquals(context['title'], 'Siddhartha')
                self.assertEqual(template.name, 'book_detail.html')
                print(template,context)


    def test_valid_authenticated_review_post_fetch_delete(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                    with c.session_transaction() as s:
                        s['profile'] = USER_PROFILE_DATA
                        s['jwt_payload'] = USER_JWT_PAYLOAD
                    c.set_cookie('localhost','token',USER_ACCESS_TOKEN)

                    data = dict(title="test", review="test", rating=4)
                    r = c.post('/book/reviews/X7YmCwAAQBAJ',data=data)
                    self.assertEqual(r.status, '302 FOUND')
                 
                    r = c.get('/book/X7YmCwAAQBAJ')
                    template, context = templates[0]
                    self.assertEqual(context['posted'], True)
                    self.assertEqual(context['my_review'].title, 'test')
                    review_id = context['my_review'].id
                    print('rid',review_id)
                    self.assertEqual(template.name, 'book_detail.html')

                    sleep(3)
                    print('edit---')
                    data = dict(title="test_edited", review="test", rating=5)
                    r = c.post('/books/X7YmCwAAQBAJ/reviews/'+str(review_id),data=data)
                    self.assertEqual(r.status, '302 FOUND')
                   
                    sleep(3)
                    r = c.delete('/books/X7YmCwAAQBAJ/reviews/'+str(review_id))
                    
                    self.assertEqual(r.status_code,200)

    def test_invalid_unauthorized_review_post(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                    
                    data = dict(title="test", review="test", rating=4)
                    r = c.post('/book/reviews/X7YmCwAAQBAJ',data=data)
                    template, context = templates[0]
                    self.assertEquals(template.name, 'errors/401.html')

                    

    def test_invalid_unauthorized_review_patch(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                    data = dict(title="test_edited", review="test", rating=5)
                    r = c.post('/books/X7YmCwAAQBAJ/reviews/22',data=data)
                    template, context = templates[0]
                    
                    self.assertEquals(template.name, 'errors/401.html')
                   
                       
    def test_invalid_unauthorized_review_delete(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                    r = c.delete('/books/X7YmCwAAQBAJ/reviews/22')
                    template, context = templates[0]
                    self.assertEquals(template.name, 'errors/401.html')

    def test_invalid_admin_index(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                    r = c.get('/admin/')
                    template, context = templates[0]
                    self.assertEqual(template.name, 'errors/401.html')

    def test_invalid_admin_fetch_users(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                    r = c.get('/admin/users')
                    template, context = templates[0]
                    self.assertEqual(template.name, 'errors/401.html')

    def test_invalid_admin_fetch_reviews(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                    r = c.get('/admin/reviews')
                    template, context = templates[0]
                    self.assertEqual(template.name, 'errors/401.html')

    def test_invalid_admin_delete_reviews(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                    r = c.delete('/admin/reviews/33')
                    template, context = templates[0]
                    self.assertEqual(template.name, 'errors/401.html')

    def test_valid_admin_fetch_users(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                with c.session_transaction() as s:
                        s['profile'] = ADMIN_PROFILE_DATA
                        s['jwt_payload'] = ADMIN_JWT_PAYLOAD
                c.set_cookie('localhost','token',ADMIN_ACCESS_TOKEN)
                r = c.get('/admin/users')
                template, context = templates[0]
                self.assertEqual(template.name, 'admin/users.html')

    def test_valid_admin_fetch_reviews(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                with c.session_transaction() as s:
                        s['profile'] = ADMIN_PROFILE_DATA
                        s['jwt_payload'] = ADMIN_JWT_PAYLOAD
                c.set_cookie('localhost','token',ADMIN_ACCESS_TOKEN)
                r = c.get('/admin/reviews')
                template, context = templates[0]
                self.assertEqual(template.name, 'admin/reviews.html')

    def test_valid_admin_index(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                with c.session_transaction() as s:
                        s['profile'] = ADMIN_PROFILE_DATA
                        s['jwt_payload'] = ADMIN_JWT_PAYLOAD
                c.set_cookie('localhost','token',ADMIN_ACCESS_TOKEN)
                r = c.get('/admin/')
                template, context = templates[0]
                self.assertEqual(template.name, 'admin/index.html')

    def test_valid_admin_delete_reviews(self):
        with self.client() as c:
            with captured_templates(self.app) as templates:
                with c.session_transaction() as s:
                        s['profile'] = ADMIN_PROFILE_DATA
                        s['jwt_payload'] = ADMIN_JWT_PAYLOAD
                c.set_cookie('localhost','token',ADMIN_ACCESS_TOKEN)
                data = dict(title="test", review="test", rating=4)

                r = c.post('/book/reviews/X7YmCwAAQBAJ',data=data)
                self.assertEqual(r.status, '302 FOUND')
                
                r = c.get('/book/X7YmCwAAQBAJ')
                template, context = templates[0]
                self.assertEqual(context['posted'], True)
                self.assertEqual(context['my_review'].title, 'test')
                review_id = context['my_review'].id
                print('rid',review_id)
                self.assertEqual(template.name, 'book_detail.html')

                r = c.delete('/admin/reviews/'+str(review_id))
                
                self.assertEqual(r.status, '200 OK')

# # Make the tests conveniently executable
if __name__ == "__main__" :
    unittest.main()