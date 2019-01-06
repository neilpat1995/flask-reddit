from flask import render_template, url_for, redirect, flash, request
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm, CreateThreadForm, RegistrationForm
from app.models import User

from werkzeug.urls import url_parse
from datetime import datetime 

@app.route('/')
@app.route('/index')
def index():
    sample_threads = [
        {
            'title': 'Index thread 1',
            'author': 'Author 1',
            'date': 'Date 1',
            'upvotes': 1
        },
        {
            'title': 'Index thread 2',
            'author': 'Author 2',
            'date': 'Date 2',
            'upvotes': 2
        }
    ]
    
    sample_subreddits = [
        {   'id': 1,
            'name': 'AskReddit'
        },
        {   'id': 2,
            'name': 'AskScience'
        }
    ]    

    # Database query to fetch latest cross-subreddit threads...

    

    # Pass both thread and subreddit model objects returned from the database to the template
    return render_template('index.html', threads_subreddits=zip(sample_threads,sample_subreddits))

# Pass an additional 'subreddit_name' argument for header and navigation bar logic
@app.route('/r/<subreddit_name>')
def subreddit(subreddit_name):
    sample_threads = [
        {
            'title': 'Subreddit thread 1',
            'author': 'Author 1',
            'date': 'Date 1',
            'upvotes': 1
        },
        {
            'title': 'Subreddit thread 2',
            'author': 'Author 2',
            'date': 'Date 2',
            'upvotes': 2
        }
    ] 
    
    # Database query to fetch latest subreddit-specific threads...



    return render_template("subreddit.html", subreddit_name=subreddit_name, threads=sample_threads)

@app.route('/create_thread', methods=['GET', 'POST'])
@login_required
def create_thread():
    form = CreateThreadForm()
    if form.validate_on_submit():
        # Database addition here...
        thread_date = datetime.utcnow()
        flash('Requested creating new thread with title {} at {}'.format(form.title.data, thread_date))
        return redirect(url_for('index'))
    return render_template('create_thread.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        requested_user = User.query.filter_by(username = form.username.data).first()
        if requested_user:
            if requested_user.check_password(form.password.data):
                login_user(requested_user, remember = form.remember_me.data)
                request_redirect_page = request.args.get('next')
                if request_redirect_page is None or url_parse(request_redirect_page).netloc != '':
                    return redirect(url_for('index'))    
                return redirect(request_redirect_page)    
        flash('Invalid username or password. Please try again.')
        return redirect(url_for('login'))        
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account was successfully created.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
