from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
  __tablename__='users'
  
  email = db.Column(db.String(120),nullable=False,primary_key=True)
  username = db.Column(db.String(120),nullable=True)
  reviews = db.relationship('Review',backref='user')




class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String())
    author = db.Column(db.String())
    category = db.Column(db.String())
    image_link = db.Column(db.String())
    summary =db.Column(db.Text)
    reviews = db.relationship('Review',backref='book')

    def __init__(self,id,title,author,category,summary,image_link):
        self.id = id
        self.title=title
        self.author=author
        self.category=category
        self.summary=summary
        self.image_link=image_link

    def format(self):
      return  ({"title":self.title,"author":self.author})


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)
    user_email= db.Column(db.String(120),db.ForeignKey('users.email'))
    book_id= db.Column(db.String,db.ForeignKey('books.id'))
    
  

    def __repr__(self):
      return f'<Review : id={self.id} comment:{self.comment}>'
