# flask-reddit
A basic implementation of Reddit using Flask.

NOTE: The website currently uses a self-signed certificate, i.e. one not generated by a trusted CA authority, that causes a warning message to appear. Currently, you have 2 options to visit the application:
1. Bypass this warning message. I'm currently working to remove this message by getting a CA-provided certificate.
2. Run the application locally by running:
    git clone https://github.com/neilpat1995/flask-reddit.git
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    flask db upgrade
    flask run
    
    Then, navigate to localhost:5000 in your browser to view the application.
