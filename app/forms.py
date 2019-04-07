from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Thread
from flask_babel import _, lazy_gettext as _l

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class CreateThreadForm(FlaskForm):
    subreddit = StringField(_l('Subreddit'), validators=[DataRequired()])
    title = StringField(_l('Title'), validators=[DataRequired(), Length(min=16, max=128)])
    body = TextAreaField(_l('Body'), validators=[DataRequired(), Length(max=256)])
    submit = SubmitField(_l('Submit'))

    def validate_title(self, title):
        thread = Thread.query.filter_by(title = title.data).first()
        if thread is not None:
            raise ValidationError(_('The specified thread title is already in use.'))

class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=8, max=64)])
    email = StringField(_l('Email'), validators=[DataRequired(), Email(), Length(max=64)])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    confirm_password = PasswordField(_l('Confirm Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Submit'))

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()
        if user is not None:
            raise ValidationError(_('The specified username is already in use.'))

    def validate_email(self, email):
        user = User.query.filter_by(email = email.data).first()
        if user is not None:
            raise ValidationError(_('The specified email address is already in use.'))

class CreateCommentForm(FlaskForm):
    body = TextAreaField(_l('Enter Your Comment'), validators=[DataRequired(), Length(max=256)])
    submit = SubmitField(_l('Submit'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email(), Length(max=64)])
    submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('New Password'), validators=[DataRequired()])
    confirm_password = PasswordField(_l('Verify New Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Reset Password'))
