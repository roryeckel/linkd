"""
Link shortening webserver which records basic analytics such as IP address
"""
__author__ = 'Rory Eckel'
__version__ = '1'

from flask import Flask, redirect, abort, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(
    app,
    session_options={
        'autocommit': True,
        'autoflush': True})

class Link(db.Model):
    """Shortened URL with path"""
    path = db.Column(db.String(256), primary_key=True)
    url = db.Column(db.String(2048), unique=True, nullable=False)
    access_log = db.relationship('AccessLog')

class AccessLog(db.Model):
    """Access logs for Link"""
    path = db.Column(db.String(256), db.ForeignKey('link.path'), primary_key=True, nullable=False)
    ip = db.Column(db.String(45), primary_key=True, nullable=False)
    when = db.Column(db.DateTime(), primary_key=True, nullable=False, default=datetime.utcnow)

    def __init__(self, path, ip):
        """Construct new log"""
        self.path = path
        self.ip = ip

@app.before_first_request
def init():
    """Initialize db"""
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def linkd(path):
    """Catch all paths: index template or link redirect with logging"""
    if not path:
        return render_template(
            'index.html',
            links=Link.query.count(),
            visits=AccessLog.query.count())
    link = Link.query.filter_by(path = path).first()
    if link:
        db.session.add(AccessLog(path, request.remote_addr))
        db.session.flush()
        return redirect(link.url)
    abort(404)

if __name__ == "__main__":
    app.run()