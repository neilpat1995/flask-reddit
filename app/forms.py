from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateThreadForm(FlaskForm):
    subreddit = StringField('Subreddit', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    body = StringField('Body', validators=[DataRequired()])
    submit = SubmitField('Sign In')
