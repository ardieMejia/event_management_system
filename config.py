import os
import sys
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ...
    # print("Goodbye cruel world!", file=sys.stderr)
    # print(os.environ['YOURAPPLICATION_MODE'], file=sys.stderr)
    
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # UPLOAD_FOLDER = './storage'
    ALLOWED_EXTENSIONS = {'png', 'pdf', 'jpg', 'jpeg'}

    SQLALCHEMY_ENGINE_OPTIONS = {
        # 'pool': QueuePool(creator),
        # 'pool_size': 10,
        # 'pool_recycle': 120,
        # 'pool_pre_ping': True
        # 'idle_in_transaction_session_timeout': 1200000,
        # 'idle_session_timeout': 1200000,
        # 'poolclass' : NullPool,
        'connect_args' : {"connect_timeout": 300}
    }
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    if os.environ.get('YOURAPPLICATION_MODE') == "production":
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

        
    UPLOAD_FOLDER = "storage"
    if os.environ.get('YOURAPPLICATION_MODE') == "production":
        UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')
        
