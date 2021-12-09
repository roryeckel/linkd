from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'linkd'
mysql = MySQL(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def linkd(path):
    with mysql.connection.cursor() as cur:
        cur.execute("""SELECT Long WHERE Short = ?""", (path,))
        result = cur.fetchall()
        print(result)

if __name__ == "__main__":
    app.run()