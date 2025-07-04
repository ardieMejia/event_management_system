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
        
    EXPIRY_PERIOD = 1 # 730 hours is 1 month
    if os.environ.get('YOURAPPLICATION_MODE') == "production":
        EXPIRY_PERIOD = os.environ.get('EXPIRY_PERIOD')


    ADMIN_ID = "terry"
    ADMIN_EMAIL = "wan.ardie.mejia@gmail.com"
    ADMIN_PASSWORD = "password"
    if os.environ.get('YOURAPPLICATION_MODE') == "production":
        ADMIN_ID = "terry"
        ADMIN_EMAIL = "wan_ahmad_ardie@yahoo.com"
        ADMIN_PASSWORD = "password"

        

    TOKEN_MAX_AGE = 1200 # 1200 is 20 min, 10800 is 3 hours
    if os.environ.get('YOURAPPLICATION_MODE') == "production":
        TOKEN_MAX_AGE = os.environ.get('TOKEN_MAX_AGE')        
        

    # # these refer to SMTP settings
    # app.config['MAIL_PASSWORD'] = "rppfxeiuwqrxjilk"

    MAIL_SERVER = 'smtp.mail.yahoo.com'  # e.g., 'smtp.gmail.com'
    MAIL_PORT = 587  # or 465 for SSL
    MAIL_USE_TLS = True  # Set to False if using SSL (port 465)
    MAIL_USE_SSL = False  # Set to True if using SSL (port 465)
    MAIL_USERNAME = 'wan_ahmad_ardie@yahoo.com'
    MAIL_PASSWORD = 'rppfxeiuwqrxjilk'
    MAIL_DEFAULT_SENDER = 'wan_ahmad_ardie@yahoo.com' # Optional default sender




        
