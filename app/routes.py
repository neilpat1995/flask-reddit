from flask import render_template, url_for, redirect, flash, request, session, g, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_babel import _, get_locale

from app import app, db
from app.forms import LoginForm, CreateThreadForm, RegistrationForm, CreateCommentForm, ResetPasswordRequestForm, ResetPasswordForm, SearchForm, CreateSubredditForm
from app.models import User, Thread, Comment, Subreddit
from app.email import send_password_reset_email
from app.translate import translate

from werkzeug.urls import url_parse
from datetime import datetime 
from guess_language import guess_language
from sqlalchemy.exc import OperationalError

@app.before_request
def before_request():
    g.search_form = SearchForm()
    g.locale = str(get_locale())

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

    return render_template('index.html', threads=threads, prev_url=prev_url, next_url=next_url, page_num = request.args.get('page', 1, int))

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
    return render_template("subreddit.html", page_title=_('Reddit - %(subreddit_name)s', subreddit_name=subreddit_name), subreddit_name=subreddit_name, threads=subreddit_threads, prev_url=prev_url, next_url=next_url, page_num = request.args.get('page', 1, int))

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
    prev_url = url_for('user', username=username, page=user_threads_page.prev_num) if user_threads_page.has_prev else None
    next_url = url_for('user', username=username, page=user_threads_page.next_num) if user_threads_page.has_next else None
    user_threads = user_threads_page.items
    return render_template("user.html", page_title=_('Reddit - u/%(username)s', username=username), username=username, user_threads=user_threads, prev_url=prev_url, next_url=next_url, page=request.args.get('page', 1, int))

@app.route('/create_thread', methods=['GET','POST'])
@login_required
def create_thread():
    form = CreateThreadForm()
    if form.validate_on_submit():
        thread_language = guess_language(form.body.data)
        if thread_language == 'UNKNOWN' or len(thread_language) > 5:
            thread_language = ''
        thread = Thread(title=form.title.data, body=form.body.data, user=current_user, language=thread_language, subreddit=Subreddit.query.filter_by(name=form.subreddit.data).first())
        db.session.add(thread)
        db.session.commit() 
        return redirect(session['prior_thread_create_page'])
    return render_template('create_thread.html', form=form, page_title=_('Reddit - Create Thread'))

@app.route('/thread/<thread_title>')
def view_thread(thread_title):
    session['current_thread_title'] = thread_title
    # Check if upvote or downvote on thread was selected
    is_upvote = request.args.get('is_upvote', type=int)

    if is_upvote is not None:
        thread = Thread.query.filter_by(title = thread_title).first()
        thread.upvotes = thread.upvotes + is_upvote
        db.session.commit()
        return redirect(url_for('view_thread', thread_title=_(thread_title)))

    thread = Thread.query.filter_by(title=thread_title).first()
    thread_comments = Comment.query.filter_by(thread=thread).order_by(Comment.date.desc())
    
    return render_template('thread.html', thread=thread, page_title=_('Reddit - %(subreddit_name)s - %(thread_title)s', subreddit_name=thread.subreddit.name, thread_title=thread.title), subreddit_name = thread.subreddit.name, comments=thread_comments) 

@app.route('/post_comment', methods=['GET','POST'])
@login_required
def add_comment():
    form = CreateCommentForm()
    if form.validate_on_submit():
        comment_language = guess_language(form.body.data)
        if comment_language == 'UNKNOWN' or len(comment_language) > 5:
            comment_language = ''
        comment = Comment(body=form.body.data, user=current_user, language=comment_language, thread=Thread.query.filter_by(title=session['current_thread_title']).first())
        db.session.add(comment)
        db.session.commit()    
        return redirect(url_for('view_thread', thread_title=session['current_thread_title']))
    return render_template('comment.html', form=form, page_title=_('Reddit - Post a Comment'))

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
                current_user.last_sign_in = datetime.utcnow()
                db.session.commit()
                request_redirect_page = request.args.get('next')
                if request_redirect_page is None or url_parse(request_redirect_page).netloc != '':
                    return redirect(url_for('index'))
                return redirect(request_redirect_page)    
        flash(_('Invalid username or password. Please try again.'))
        return redirect(url_for('login'))        
    return render_template('login.html', form=form, page_title=_('Reddit - Log In'))

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
        flash(_('Your account was successfully created.'))
        return redirect(url_for('login'))
    return render_template('register.html', form=form, page_title=_('Reddit - Register'))

@app.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('Check your email for instructions on how to reset your password.'))
        return redirect(url_for('login'))    
    return render_template('reset_password_request.html', form=form, page_title=_('Reddit - Reset Password Request'))

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
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form, page_title=_('Reddit - Reset Password'))

@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form.getlist('text[]'),
                                      request.form['dest_language'])})

@app.route('/translate_thread', methods=['POST'])
@login_required
def translate_thread_text():
    if request.form.has_key('body_text'):
        # Perform title and body translations
        return jsonify({'title_text': translate(request.form['title_text'], request.form['dest_language']),
                        'body_text': translate(request.form['body_text'], request.form['dest_language'])})
    else:
        # Perform only title translation
        return jsonify({'title_text': translate(request.form['title_text'], request.form['dest_language'])})

@app.route('/search', methods=['GET'])
def search():
    print 'Hit the /search route!'
    if not g.search_form.validate():
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    target_index = request.args.get('index', 'thread')
    if target_index == 'thread':
        results, total = Thread.search(g.search_form.q.data, page, app.config['POSTS_PER_PAGE'])
        print 'Called Thread.search(), total results = {}'.format(total)
    elif target_index == 'user':
        results, total = User.search(g.search_form.q.data, page, app.config['POSTS_PER_PAGE'])
        print 'Called User.search(), total results = {}'.format(total)
    elif target_index == 'subreddit':
        results, total = Subreddit.search(g.search_form.q.data, page, app.config['POSTS_PER_PAGE'])
        print 'Called Subreddit.search(), total results = {}'.format(total)
    else:
        return render_template('404.html')
    
    results = results.all()
    next_url = url_for('search', index=target_index, q=g.search_form.q.data, page=page + 1) if total > page * app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('search', index=target_index, q=g.search_form.q.data, page=page - 1) if page > 1 else None
    return render_template('search.html', title=_('Search'), results=results, next_url=next_url, prev_url=prev_url, query=g.search_form.q.data, query_language = guess_language(g.search_form.q.data), index=target_index)

@app.route('/view_subreddits', methods=['GET'])
def view_subreddits():
    page_num = request.args.get('page', 1, type=int)
    subreddits_page = Subreddit.query.paginate(page_num, app.config['POSTS_PER_PAGE'], True)
    subreddits_items = subreddits_page.items
    next_url = url_for('view_subreddits', page=page_num+1) if subreddits_page.has_next else None
    prev_url = url_for('view_subreddits', page=page_num-1) if subreddits_page.has_prev else None
    return render_template('view_subreddits.html', subreddits=subreddits_items, next_url=next_url, prev_url=prev_url)

@app.route('/create_subreddit', methods=['GET','POST'])
@login_required
def create_subreddit():
    form = CreateSubredditForm()
    if form.validate_on_submit():
        subreddit_language = guess_language(form.description.data)
        if subreddit_language == 'UNKNOWN' or len(subreddit_language) > 5:
            subreddit_language=''
        new_subreddit = Subreddit(name=form.name.data, description=form.description.data, language=subreddit_language)
        db.session.add(new_subreddit)
        db.session.commit()
        return redirect(session['prior_thread_create_page'])     
    return render_template('create_subreddit.html', form=form, page_title=_('Reddit - Create Subreddit'))
