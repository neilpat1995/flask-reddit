from flask import render_template, url_for, redirect, flash
from app import app
from app.forms import LoginForm, CreateThreadForm

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

# Pass an additional 'subreddit_name' argument for headeri and navigation bar logic
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
    form = LoginForm()
    if form.validate_on_submit():
        flash('Requested log in for user {}, remember_me = {}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', form=form)
