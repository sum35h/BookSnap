from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, TextAreaField,DateTimeField,TextField,BooleanField,IntegerField
from wtforms.validators import DataRequired


class ReviewForm(Form):
    title = StringField(
        'title', validators=[DataRequired()],
    )
    rating = SelectField(
        'rating', validators=[DataRequired()],
        choices=[# enum restriction implemented
        (1,'I hated it'),
        (2,'I did notlike it'),
        (3,'It was OK'),
        (4,'I liked it'),
        (5,'I loved it'),

        ]
    )
    review = TextAreaField(
        'review', validators=[DataRequired(),]
    )
    
