from flask import Flask, redirect, abort
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'linkd'
mysql = MySQL(app)

@app.before_first_request
def init():
    with mysql.connection.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS linkd (
            Path VARCHAR(256) PRIMARY KEY,
            URL VARCHAR(2048) NOT NULL);""")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def linkd(path):
    with mysql.connection.cursor() as cur:
        cur.execute("""SELECT URL FROM linkd WHERE Path = %s""", (str(path),))
        url = cur.fetchone()
        if url:
            return redirect(url[0])
        else:
            abort(404)

if __name__ == "__main__":
    app.run()