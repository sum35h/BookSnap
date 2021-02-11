from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
  __tablename__='users'
  
  id = db.Column(db.String(),nullable=False,primary_key=True)
  username = db.Column(db.String(120),nullable=True)
  reviews = db.relationship('Review',backref='user')

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def __repr__(self):
      return f'<User : id={self.id} username:{self.username}>'

  def format(self):
      return  ({
        "id":self.id,
        "username":self.username,
        "reviews":self.reviews
        })





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

    def insert(self):
      db.session.add(self)
      db.session.commit()
  
    def update(self):
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()

    def __repr__(self):
      return f'<Book : id={self.id} title:{self.title} author:{self.author}>'

    def format(self):
      return  ({
        "id":self.id,
        "title":self.title,
        "author":self.author,
        "category":self.category,
        "summary":self.summary,
        "image_link":self.image_link
        })


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    edited = db.Column(db.DateTime)
    title = db.Column(db.String(120))
    comment = db.Column(db.Text)
    rating = db.Column(db.Integer)
    user_id = db.Column(db.String,db.ForeignKey('users.id'))
    book_id= db.Column(db.String,db.ForeignKey('books.id'))

    def insert(self):
      db.session.add(self)
      db.session.commit()
    
    def update(self):
      db.session.commit()

    def delete(self):
      db.session.delete(self)
      db.session.commit()
    def __repr__(self):
      return f'<Review : id={self.id} title:{self.title} comment:{self.comment}>'

    def format(self):
      return  ({
        "id":self.id,
        "created":self.created,
        "edited":self.edited,
        "comment":self.comment,
        "rating":self.rating,
        "user_id":self.user_id,
        "book_id":self.book_id,
        })