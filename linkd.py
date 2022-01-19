"""
Link shortening webserver which records basic analytics such as IP address
"""
__author__ = 'Rory Eckel'
__version__ = '1'

from flask import Flask, redirect, abort, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['LINKD_SECRET'] = os.getenv('LINKD_SECRET')
db = SQLAlchemy(
    app,
    session_options={
        'autocommit': True,
        'autoflush': True})

class Link(db.Model):
    """Shortened URL with path"""
    __tablename__ = 'link'
    path = db.Column(db.String(256), primary_key=True)
    url = db.Column(db.String(2048), nullable=False)

    def __init__(self, path, url):
        """Construct new link"""
        self.path = path
        self.url = url

class AccessLog(db.Model):
    """Access logs for Link"""
    __tablename__ = 'access_log'
    path = db.Column(db.String(256), db.ForeignKey('link.path', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True, nullable=False)
    link = db.relationship(Link, backref=db.backref('access_log', cascade='all, delete-orphan'), lazy='joined')
    ip = db.Column(db.String(45), primary_key=True, nullable=False)
    when = db.Column(db.DateTime(), primary_key=True, nullable=False, default=datetime.utcnow)

    def __init__(self, path, ip):
        """Construct new log"""
        self.path = path
        self.ip = ip

if not db:
    raise Exception('Unable to open SQLALCHEMY_DATABASE_URI')
db.create_all()

def secret_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.values.get('LINKD_SECRET') != app.config['LINKD_SECRET']:
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
def index():
    """Index template"""
    if request.values.get('LINKD_SECRET') == app.config['LINKD_SECRET']:
        return Link.query.all()
    return render_template(
        'index.html',
        links=Link.query.count(),
        visits=AccessLog.query.count())

@app.route('/<path:path>', methods=['POST'])
@secret_required
def linkd_post(path):
    url = request.form.get('url')
    if not url:
        abort(400)
    link = Link.query.filter_by(path=path).first()
    if link:
        link.url = url
    else:
        db.session.add(Link(path, url))
    db.session.flush()
    return '', 204

@app.route('/<path:path>', methods=['GET'])
def linkd_get(path):
    """Catch all subpaths: link redirect with logging"""
    link = Link.query.filter_by(path=path).first()
    if not link:
        abort(404)
    db.session.add(AccessLog(path, request.remote_addr))
    db.session.flush()
    return redirect(link.url)

@app.route('/<path:path>', methods=['DELETE'])
@secret_required
def linkd_delete(path):
    link = Link.query.filter_by(path=path).first()
    if not link:
        abort(404)
    db.session.delete(link)
    db.session.flush()
    return '', 204

if __name__ == "__main__":
    app.run()