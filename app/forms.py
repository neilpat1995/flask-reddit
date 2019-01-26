from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Thread

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class CreateThreadForm(FlaskForm):
    subreddit = StringField('Subreddit', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired(), Length(min=16, max=128)])
    body = StringField('Body', validators=[DataRequired(), Length(max=256)])
    submit = SubmitField('Submit')

    def validate_title(self, title):
        thread = Thread.query.filter_by(title = title.data).first()
        if thread is not None:
            raise ValidationError('The specified thread title is already in use.')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=8, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError('The specified username is already in use.')

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError('The specified email address is already in use.')
