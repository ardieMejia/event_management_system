import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # ...
    TEMPLATES_FOLDER = os.environ.get('TEMPLATES_FOLDER') or \
        os.path.join(basedir, 'templates2')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
