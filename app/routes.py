from flask import render_template, url_for, redirect, flash, request, session
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm, CreateThreadForm, RegistrationForm
from app.models import User, Thread, Subreddit

from werkzeug.urls import url_parse
from datetime import datetime 

@app.route('/')
@app.route('/index')
def index():
    session['prior_thread_create_page'] = url_for('index')

    threads = Thread.query.all()
    authors = [thread.user for thread in threads]
    subreddits = [thread.subreddit for thread in threads]

    return render_template('index.html', threads_authors_subreddits=zip(threads, authors, subreddits))

@app.route('/r/<subreddit_name>')
def subreddit(subreddit_name):
    session['prior_thread_create_page'] = url_for('subreddit', subreddit_name = subreddit_name) 
    subreddit_threads = Subreddit.query.filter_by(name = subreddit_name).first().threads
    authors = [thread.user for thread in subreddit_threads]
    return render_template("subreddit.html", subreddit_name=subreddit_name, subreddit_threads_authors=zip(subreddit_threads, authors))

@app.route('/create_thread', methods=['GET', 'POST'])
@login_required
def create_thread():
    form = CreateThreadForm()
    if form.validate_on_submit():
        thread = Thread(title=form.title.data, body=form.body.data, user=current_user, subreddit=Subreddit.query.filter_by(name=form.subreddit.data).first())
        db.session.add(thread)
        db.session.commit() 
        '''
        subreddit_redirect_page = request.args.get('subreddit_redirect_url')
        if subreddit_redirect_page is None:
            print 'Failed to pass subreddit_redirect_page'
            return redirect(url_for('index'))
        return redirect(subreddit_redirect_page)
        '''
        return redirect(session['prior_thread_create_page'])
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
