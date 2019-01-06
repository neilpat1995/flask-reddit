from app import app, db
from app.models import User, Thread, Comment, Subreddit

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Thread': Thread, 'Comment': Comment, 'Subreddit': Subreddit}
