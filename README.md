# linkd

Link shortening webserver which records basic analytics such as IP address

Built with flask and sqlalchemy

1. Set environment variables for SQLALCHEMY_DATABASE_URI and LINKD_SECRET ("admin" password)
2. Use a wsgi server on linkd.py