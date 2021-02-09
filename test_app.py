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
USER_ACCESS_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IngzOThFR1RoWUQyUS1uYzRVRWxOcSJ9.eyJpc3MiOiJodHRwczovL3N1bWVzaC1mc25kLmpwLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDFjMWY0YjM1ZmJlYjAwNmI0NWE1OGEiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjUwMDAiLCJpYXQiOjE2MTI4ODc1NTYsImV4cCI6MTYxMjg5NDc1NiwiYXpwIjoiNVByRlZPOFlCR1NISmJGNlhkdllqRnlKMk4wVlZqM3oiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTp1c2VyX3Jldmlld3MiLCJnZXQ6dXNlcl9yZXZpZXdzIiwicGF0Y2g6dXNlcl9yZXZpZXdzIiwicG9zdDp1c2VyX3Jldmlld3MiXX0.WX-6_A69nL5zU4ryeJAR8Y7YA33eyGs3Fl95TrDl0ffU_1rrrJZwOIyk9Vo3iplQ_f00cImDlraZSfuNHrTBh392CREVMyeb8gc_4NsIkVXEwlZQu9sPdo6y9r4sknQO0Wqo6tqDWK-TkM5zxyvoSfLlYfKgddsE4OOcSQno8sHaTDb2-fUqs6e-8BQYzS58Xf_D4zcXUhlsFxzz5aeUqRFCDxeG0TzWB6l-hR8euu8MDaw_ryZIDfCB1qpYEDVCAElnnXhEK47US_lXry-JCXW_rkuFnbKN-ggCCCWJ5wShQJtLkFt7gTLmZ93NyBpv-hE3x2yTY8IruxYzRAVRUw'

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
ADMIN_ACCESS_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IngzOThFR1RoWUQyUS1uYzRVRWxOcSJ9.eyJpc3MiOiJodHRwczovL3N1bWVzaC1mc25kLmpwLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw2MDIyYmVmMjNhZTlkNjAwNmNhZjc1OGIiLCJhdWQiOiJodHRwOi8vbG9jYWxob3N0OjUwMDAiLCJpYXQiOjE2MTI4ODk5MzAsImV4cCI6MTYxMjg5NzEzMCwiYXpwIjoiNVByRlZPOFlCR1NISmJGNlhkdllqRnlKMk4wVlZqM3oiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphbGxfcmV2aWV3cyIsImRlbGV0ZTp1c2VyX3Jldmlld3MiLCJnZXQ6YWRtaW4iLCJnZXQ6YWxsX3Jldmlld3MiLCJnZXQ6YWxsX3VzZXJzIiwiZ2V0OnVzZXJfcmV2aWV3cyIsInBhdGNoOnVzZXJfcmV2aWV3cyIsInBvc3Q6dXNlcl9yZXZpZXdzIl19.p9UB_pCZGeqb0LD5Td04N3un3TaJM2tx8n4kZ28EOJtcSz6J9Szm7lptBERbJyM_TwZN2rATsP3RGYV6JXXJfFPTeuL0JNMhBEoe5FCfofqsrNnaeMuuzsUjDMmQS6GQMAS3kAqW-kBtvUkVPWdA072xplslHNn8V0S__TNf9ZQdRelgzhBqedJMVKrkjip952Crcn-T2I6D5rewS0OHtEfKze3EPr75kKRc-st64Ev9l_sS4eTCIA_BUlARez3tlsMnCLNOvha9vfYIuYezrZiZ_MoYOBDSJWvp4adis8d30OdeS8-YFTovjAR51_3lcBReRQGhITqeb5snmqR-jQ'


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
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "booksnap_db"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','password','localhost:5432', self.database_name)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['TESTING'] = True
     
        # binds the app to the current context
        # with self.app.app_context():

        #     session['jwt_payload'] = 'testpayload'
           
        #     session['profile'] = {
        #         'user_id': '601c1f4b35fbeb006b45a58a',
        #         'name': "test123@gmail.com",
              
  
        # }

        
    
    def tearDown(self):
        """Executed after each test"""
        print("teardown")
        # with self.app.app_context():
        #     try:
        #         self.db.session.query(Category).delete()
        #         self.db.session.query(Question).delete()
        #         self.db.session.commit()
        #     except Exception as e:
        #         print('error',e)
        #         self.db.session.rollback()


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