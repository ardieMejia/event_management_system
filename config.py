import os
import sys
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ...
    # print("Goodbye cruel world!", file=sys.stderr)
    # print(os.environ['YOURAPPLICATION_MODE'], file=sys.stderr)
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = './storage'
    ALLOWED_EXTENSIONS = {'txt', 'png', 'pdf', 'jpg', 'jpeg'}
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    if os.environ.get('YOURAPPLICATION_MODE') == "production":
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
        
