from flask import render_template, url_for, redirect, flash, request, session
from flask_login import current_user, login_user, logout_user, login_required

from app import app, db
from app.forms import LoginForm, CreateThreadForm, RegistrationForm, CreateCommentForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Thread, Comment, Subreddit
from app.email import send_password_reset_email

from werkzeug.urls import url_parse
from datetime import datetime 

@app.route('/')
@app.route('/index')
def index():
    session['prior_thread_create_page'] = url_for('index')
    # Check if upvote or downvote on thread was selected
    thread_title = request.args.get('thread_title')
    is_upvote = request.args.get('is_upvote', type=int)

    if thread_title is not None and is_upvote is not None:
        thread = Thread.query.filter_by(title = thread_title).first()
        thread.upvotes = thread.upvotes + is_upvote
        db.session.commit()
        return redirect(url_for('index', page=request.args.get('page', 1, int)))
    
    thread_page = Thread.query.order_by(Thread.date.desc()).paginate(request.args.get('page', 1, int), app.config['POSTS_PER_PAGE'], True)
    prev_url = url_for('index', page=thread_page.prev_num) if thread_page.has_prev else None
    next_url = url_for('index', page=thread_page.next_num) if thread_page.has_next else None
    threads = thread_page.items
    authors = [thread.user for thread in threads]
    subreddits = [thread.subreddit for thread in threads]

    return render_template('index.html', threads_authors_subreddits=zip(threads, authors, subreddits), prev_url=prev_url, next_url=next_url)

@app.route('/r/<subreddit_name>')
def subreddit(subreddit_name):
    session['prior_thread_create_page'] = url_for('subreddit', subreddit_name = subreddit_name)
    # Check if upvote or downvote on thread was selected
    thread_title = request.args.get('thread_title')
    is_upvote = request.args.get('is_upvote', type=int)

    if thread_title is not None and is_upvote is not None:
        thread = Thread.query.filter_by(title = thread_title).first()
        thread.upvotes = thread.upvotes + is_upvote
        db.session.commit() 
        return redirect(url_for('subreddit', subreddit_name=subreddit_name, page=request.args.get('page', 1, int)))

    subreddit = Subreddit.query.filter_by(name = subreddit_name).first()
    subreddit_threads_page = Thread.query.filter_by(subreddit = subreddit).order_by(Thread.date.desc()).paginate(request.args.get('page', 1, int), app.config['POSTS_PER_PAGE'], True) 
    prev_url = url_for('subreddit', subreddit_name=subreddit_name, page=subreddit_threads_page.prev_num) if subreddit_threads_page.has_prev else None
    next_url = url_for('subreddit', subreddit_name=subreddit_name, page=subreddit_threads_page.next_num) if subreddit_threads_page.has_next else None
    subreddit_threads = subreddit_threads_page.items
    authors = [thread.user for thread in subreddit_threads]
    return render_template("subreddit.html", subreddit_name=subreddit_name, subreddit_threads_authors=zip(subreddit_threads, authors), prev_url=prev_url, next_url=next_url)

@app.route('/user/<username>')
def user(username):
    # Check if upvote or downvote on thread was selected
    thread_title = request.args.get('thread_title')
    is_upvote = request.args.get('is_upvote', type=int)

    if thread_title is not None and is_upvote is not None:
        thread = Thread.query.filter_by(title = thread_title).first()
        thread.upvotes = thread.upvotes + is_upvote
        db.session.commit() 
        return redirect(url_for('user', username=username, page=request.args.get('page', 1, int)))

    user = User.query.filter_by(username=username).first_or_404()
    user_threads_page = Thread.query.filter_by(user=user).order_by(Thread.date.desc()).paginate(request.args.get('page', 1, int), app.config['POSTS_PER_PAGE'], True)
    prev_url = url_for('user', username=username, page=user_threads_page.prev_num if user_threads_page.has_prev else None)
    next_url = url_for('user', username=username, page=user_threads_page.next_num if user_threads_page.has_next else None)
    user_threads = user_threads_page.items
    return render_template("user.html", username=username, user_threads=user_threads, prev_url=prev_url, next_url=next_url, page=request.args.get('page', 1, int))

@app.route('/create_thread', methods=['GET','POST'])
@login_required
def create_thread():
    form = CreateThreadForm()
    if form.validate_on_submit():
        thread = Thread(title=form.title.data, body=form.body.data, user=current_user, subreddit=Subreddit.query.filter_by(name=form.subreddit.data).first())
        db.session.add(thread)
        db.session.commit() 
        return redirect(session['prior_thread_create_page'])
    return render_template('create_thread.html', form=form)

@app.route('/thread/<thread_title>')
def view_thread(thread_title):
    session['current_thread_title'] = thread_title
    # Check if upvote or downvote on thread was selected
    is_upvote = request.args.get('is_upvote')

    if is_upvote is not None:
        thread = Thread.query.filter_by(title = thread_title).first()
        thread.upvotes = thread.upvotes + int(is_upvote)
        db.session.commit() 

    thread = Thread.query.filter_by(title=thread_title).first()
    thread_comments = Comment.query.filter_by(thread=thread).order_by(Comment.date.desc())
    return render_template('thread.html', thread=thread, comments=thread_comments, subreddit=thread.subreddit, author=thread.user)

@app.route('/post_comment', methods=['GET','POST'])
@login_required
def add_comment():
    form = CreateCommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, user=current_user, thread=Thread.query.filter_by(title=session['current_thread_title']).first())
        db.session.add(comment)
        db.session.commit()    
        return redirect(url_for('view_thread', thread_title=session['current_thread_title']))
    return render_template('comment.html', form=form)

@app.route('/login', methods=['GET','POST'])
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

@app.route('/register', methods=['GET','POST'])
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

@app.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions on how to reset your password.')
        return redirect(url_for('login'))    
    return render_template('reset_password_request.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
