import os
import sys
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ...
    # print("Goodbye cruel world!", file=sys.stderr)
    # print(os.environ['YOURAPPLICATION_MODE'], file=sys.stderr)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    if os.environ.get('YOURAPPLICATION_MODE') == "production":
        SQLALCHEMY_DATABASE_URI = "postgresql://tailwind_test_postgres_user:Cf2tRDhIrySSXRpANQIbrgkyqCzSWkSz@dpg-cve40i3qf0us738eth40-a.singapore-postgres.render.com/tailwind_test_postgres"
        SECRET_KEY = os.environ.get('SECRET_KEY')
        
