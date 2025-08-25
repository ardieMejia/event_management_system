import logging
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
# from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
# environment = Environment(loader=FileSystemLoader("templates/"))
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError, DataError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_paginate import Pagination, get_page_args
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.orm import close_all_sessions
import os
import time
import pandas as pd
from io import StringIO, BytesIO
import datetime
import pytz
# from c_validation_funcs import convert_nan_to_string
from c_validation_funcs import validate_before_saving
import uuid
import filetype
from flask_wtf.csrf import CSRFProtect
from functools import wraps
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer as Serializer
import sys
from logging.config import dictConfig
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import json


dictConfig({
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout", # Or ext://sys.stderr
            "formatter": "default",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]}, # Set root level to INFO
})

app = Flask(__name__)   # Flask constructor
    
with app.app_context():
    app.logger.setLevel(logging.DEBUG) # Or DEBUG more verbose than INFO
    app.config.from_object(Config)
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    bcrypt = Bcrypt(app)
    login = LoginManager(app)
    mail = Mail(app)
    csrf = CSRFProtect(app)
    
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "30 per hour"],
        storage_uri="memory://",
    )

# @app.teardown_request
# def teardown_request(response_or_exc):
#     db.session.remove()

# @app.teardown_appcontext
# def teardown_appcontext(response_or_exc):
#     db.session.remove()


# app.config['TEMPLATES_AUTO_RELOAD'] = True


from Models.declarative import EventListing # ===== remove this
import sqlalchemy as sa
# app.app_context().push()
from model import Event, Member, File, FormQuestion, EventMember, FormQuestionAnswers, FormQuestionSubgroup, FormQuestionAnswersDeleted, EventDeleted, Withdrawal
# Session = sessionmaker(bind=db.engine)


from c_templater import C_templater

# ========== CSV
import csv


# ========== CSV




from c_mapper import C_mapper

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', whatHappened="Please login with your admin account"))
        elif not current_user.isAdmin:
            return redirect(url_for('login', whatHappened="Only admins allowed passed this point"))        
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login', whatHappened="Please login"))
        return f(*args, **kwargs)
    return decorated_function


def create_databases():
    """Creates databses and injects the main admin account into the user db"""
    with app.app_context():
        db.create_all()
        if not db.session.execute(
            db.select(Member).filter_by(isAdmin=True)
        ).scalar_one_or_none():
            admin = Member(
                mcfId=app.config["ADMIN_ID"],
                email=app.config["ADMIN_EMAIL"],
                isAdmin=True,
            )
            admin.set_password(password=app.config["ADMIN_PASSWORD"])
            db.session.add(admin)
            db.session.commit()
            db.close_all_sessions()

with app.app_context():
    close_all_sessions()
    db.engine.dispose()    
    db.drop_all()
    create_databases()
    db.session.commit()
# =======
    
start=0
end=0

@contextmanager
def session_scope():
    """Provides a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    
# A decorator used to tell the application 
# which URL is associated function 





@app.before_request
def make_session_permanent():
    db.session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)


def tryRemoveMcfFile(filename):
    # myfile = "/tmp/foo.txt"
    # If file exists, delete it.
    if os.path.isfile(filename):
        os.remove(filename)
    else:
        pass



def isFileUploaded(filename):
    if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        return True
    return False


def isFileOversized(filename):

    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    if len(df) > 502:
        return True
    return False
    


@app.route('/single-member-fide/<mcfId>', methods = ['GET'])
@login_required
def single_member_fide(mcfId):

    whatHappened = request.args.get("whatHappened")
    if not whatHappened:
        whatHappened=""
    query = sa.select(Member).where(Member.mcfId == mcfId)
    m = db.session.scalar(query)
    return render_template("single-member-fide.html", m=m, whatHappened=whatHappened)
# return m


@app.route('/update-fide', methods = ['POST'])
@login_required
def update_fide():
    mcfId = request.args.get("mcfId")
    # query = sa.select(Member).where(Member.mcfId == mcfId)
    # m = db.session.scalar(query)
    # m = db.session(Member).where(Member.mcfId == mcfId )


    statement = db.select(Member).where(Member.mcfId == mcfId)
    m = db.session.scalars(statement).first()
    if m.isAdmin:
        return redirect(url_for("member_front", whatHappened="Info: admin ans not saved to avoid spoiling ans data"))
    m.fideId = request.form['fideId']
    m.fideName = request.form['fideName']
    m.fideRating = request.form['fideRating']
    # TODO: do something about this one

    errorsList = m.isDataInvalid(p_fideId=m.fideId, p_fideRating=m.fideRating)
    if errorsList:            
        return redirect(url_for('single_member_fide', mcfId=mcfId, whatHappened=",".join(errorsList)))

        # return redirect(url_for('member_front', whatHappened=whatHappened))
        # return C_templater.custom_render_template(errorTopic="Invalid Input Error", errorsList=errorsList, isTemplate=True)
    

    db.session.add(m)
    try:
        db.session.commit()
        whatHappened = "new FIDE saved"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        # return C_templater.custom_render_template(errorTopic="DB-API IntegrityError", errorsList=[i._message], isTemplate=True)
        whatHappened = "IntegrityError: Something went wrong (most likely FIDE already exists)"
        app.logger.info(f"IntegrityError: {str(i)}")
        
    except DataError as d:
        db.session.rollback()
        # return C_templater.custom_render_template(errorTopic="DB API DataError", errorsList=[d._message], isTemplate=True)
        whatHappened = "something went wrong"


    # db.session.close() # we are eager to close session after last times error in production
    

    return redirect(url_for('member_front', whatHappened=whatHappened))
    # return render_template("member-front.html", m=m, tournamentRegistered=tr, tournamentOptions=es, whatHappened=whatHappened)



@app.route('/event-create')
@admin_required
def event_create():

    
    return render_template("event-create.html", dl=Event.disciplinesList, tl=Event.typeList, el=Event.eligibilityList, ll=Event.limitationList, rl=Event.roundsList, tcl=Event.timeControlList)


@app.route('/member-update-page/<mcfId>')
@admin_required
def member_update_page(mcfId):

    return redirect(url_for('main_page', whatHappened="Info: This feature has been disabled"))

    # query = sa.select(Member).where(Member.mcfId == mcfId)
    # m = db.session.scalar(query)

    # query = sa.select(Event)
    # es = db.session.scalars(query).all()

    
    # return render_template("member-update-page.html", m=m, es=es)



@app.route('/create-event', methods = ['POST'])
@admin_required
def create_event():

    EventDeleted.delete_expired()
    
    # with session_scope() as session:
    e = Event(tournamentName=request.form['tournamentName'], startDate=request.form['startDate'], endDate=request.form['endDate'], discipline=request.form['discipline'], type=request.form['type'], eligibility=request.form['eligibility'], limitation=request.form['limitation'], rounds=request.form['rounds'], timeControl=request.form['timeControl'], withdrawalClause=request.form['withdrawalClause'])

    
    # if e.old_isDataInvalid(p_tournameName=e.tournamentName, p_startDate=e.startDate, p_endDate=e.endDate, p_discipline=e.discipline):
    #     errorsList = e.old_isDataInvalid(p_tournameName=e.tournamentName, p_startDate=e.startDate, p_endDate=e.endDate, p_discipline=e.discipline)
    #     return C_templater.custom_render_template(errorTopic="Invalid Input Error", errorsList=errorsList, isTemplate=True)
    
    errorsList = e.isDataInvalid(p_tournameName=e.tournamentName, p_startDate=e.startDate, p_endDate=e.endDate, p_discipline=e.discipline)
    if errorsList:
        # errorsList = e.isDataInvalid(p_tournameName=e.tournamentName, p_startDate=e.startDate, p_endDate=e.endDate, p_discipline=e.discipline)
        # return C_templater.custom_render_template(errorTopic="Invalid Input Error", errorsList=errorsList, isTemplate=True)
        errorMessage = " -- "+" -- ".join(errorsList)
        return redirect(url_for('find_events', whatHappened="Error: "+errorMessage))


    e.id = e.set_id()
    db.session.add(e)
    # db.session.commit()

    
    
    try:
        db.session.commit()
    except IntegrityError as i:
        db.session.rollback()
        return redirect(url_for('find_events', whatHappened="Error: "+i._message()))
        

    return redirect(url_for('find_events'))

        # return render_template("confirmed-event-created.html", e=e)


@app.route('/create-member', methods = ['POST'])
@admin_required
def create_member():
    m = Member(
        mcfId=request.form['mcfId'],
        mcfName=request.form['mcfName'],
        gender=request.form['gender'],
        yearOfBirth=request.form['yearOfBirth'],
        state=request.form['state'],
        nationalRating=request.form['nationalRating'],
        # events=request.form['events'] ========== we delegate events to an update page, make things much simpler
    )
    
    db.session.add(m)
    
    try:
        db.session.commit()
    except IntegrityError as i:
        db.session.rollback()
        return redirect(url_for('find_members', whatHappened=f"IntegrityError: {i}"))
        # return C_templater.custom_render_template(errorTopic="DB-API IntegrityError", errorsList=[i._message], isTemplate=True)
    # example of final form ===== return c_templater("Data entry error", "tournament name duplicate", "error.html")
        
    # app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))
    # app.logger.info(m)
    # app.logger.info('========== event ==========')


    # return C_templater.custom_render_template("Successfully saved", i._message())
    return redirect('/members', whatHappened="New member successfully saved")




@app.route('/kill-event', methods=['POST'])
@admin_required
def kill_event():
    id = request.form['id']
    deleted_at = request.form['deleted_at']

    if deleted_at:
        stmt = sa.delete(EventDeleted).where(EventDeleted.id == id)
        db.session.execute(stmt)
        
        try:
            db.session.commit()
            whatHappened = "expired event KILLED"
        except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
            db.session.rollback()
            whatHappened=f"IntegrityError: {i}"
        
        return redirect(url_for('find_events', whatHappened=whatHappened))
        

    
    stmt = sa.delete(Event).where(Event.id == id)
    db.session.execute(stmt)

    stmt = sa.delete(EventMember).where(EventMember.eventId == id)
    db.session.execute(stmt)

    stmt = sa.delete(FormQuestion).where(FormQuestion.eventId == id)
    db.session.execute(stmt)
    
    stmt = sa.delete(FormQuestionSubgroup).where(FormQuestionSubgroup.eventId == id)
    db.session.execute(stmt)
    
    stmt = sa.delete(FormQuestionAnswers).where(FormQuestionAnswers.eventId == id)
    db.session.execute(stmt)
    
    stmt = sa.delete(FormQuestionAnswersDeleted).where(FormQuestionAnswersDeleted.eventId == id)
    db.session.execute(stmt)
    
    stmt = sa.delete(File).where(File.eventId == id)
    db.session.execute(stmt)

    try:
        db.session.commit()
        whatHappened = "Success: This event and its associated events-members, formquestions, formquestionssubgroup, formquestionanswers, overwritten answers & upload logs KILLED"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened="Error: "+i._message()



    
    query = sa.select(Event)
    es = db.session.scalars(query).all()

    
    # return render_template("events.html", es=es, whatHappened="Event successfully killed")
    return redirect(url_for('find_events', whatHappened=whatHappened))



@app.route('/expire-event/<int:id>')
@admin_required
def expire_event(id):


    statement = db.select(Event).where(Event.id == id)
    e = db.session.scalars(statement).first()

    ed = EventDeleted(
        id = e.id,
        tournamentName = e.tournamentName,
        startDate = e.startDate,
        endDate = e.endDate,
        discipline = e.discipline,
        type = e.type,
        eligibility = e.eligibility,
        limitation = e.limitation,
        rounds = e.rounds,
        timeControl = e.timeControl,
        withdrawalClause = e.withdrawalClause,
    )
    db.session.add(ed)
    
    stmt = sa.delete(Event).where(Event.id == id)
    db.session.execute(stmt)                                   
    

    stmt = sa.delete(EventMember).where(EventMember.eventId == id)
    db.session.execute(stmt)


    stmt = sa.delete(FormQuestion).where(FormQuestion.eventId == id)
    db.session.execute(stmt)




    
    stmt = sa.delete(FormQuestionSubgroup).where(FormQuestionSubgroup.eventId == id)
    db.session.execute(stmt)


    stmt = sa.delete(FormQuestionAnswers).where(FormQuestionAnswers.eventId == id)
    db.session.execute(stmt)


    
    stmt = sa.delete(FormQuestionAnswersDeleted).where(FormQuestionAnswersDeleted.eventId == id)
    db.session.execute(stmt)
    
    stmt = sa.delete(File).where(File.eventId == id)
    db.session.execute(stmt)


    try:
        db.session.commit()
        whatHappened = "event EXPIRED and its associated events-members, formquestions, formquestionssubgroup, formquestionanswers, overwritten answers & upload logs DELETED"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened=f"IntegrityError: {i}"
        return redirect(url_for('find_events', whatHappened=whatHappened))

    query = sa.select(Event)
    es = db.session.scalars(query).all()

    
    # return render_template("events.html", es=es, whatHappened="Event successfully killed")
    return redirect(url_for('find_events', whatHappened=whatHappened))



@app.route('/kill-events')
@admin_required
def kill_events():

    whatHappened = ""    

    stmt = sa.delete(Event)
    db.session.execute(stmt)

    
    try:
        db.session.commit()
        whatHappened = "all events deleted, "
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened = f"IntegrityError: {i}"

        
    stmt = sa.delete(EventMember)
    db.session.execute(stmt)

    try:
        db.session.commit()
        whatHappened = "all member-events relations deleted"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened = f"IntegrityError: {i}"

    stmt = sa.delete(FormQuestion)
    db.session.execute(stmt)

    try:
        db.session.commit()
        whatHappened = "all member-events rel, formquestion deleted"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened = f"IntegrityError: {i}"

        
    stmt = sa.delete(FormQuestionSubgroup)
    db.session.execute(stmt)

    try:
        db.session.commit()
        whatHappened = "all member-events rel, formquestion, formquestionsubgroup deleted"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened = f"IntegrityError: {i}"

    stmt = sa.delete(FormQuestionAnswers)
    db.session.execute(stmt)

    try:
        db.session.commit()
        whatHappened = "all member-events rel, formquestion, formquestionsubgroup, answers deleted"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened = f"IntegrityError: {i}"

    stmt = sa.delete(FormQuestionAnswersDeleted)
    db.session.execute(stmt)

    try:
        db.session.commit()
        whatHappened = "all member-events rel, formquestion, formquestionsubgroup, answers & overwritten answers deleted"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened = f"IntegrityError: {i}"

    
    query = sa.select(Event)
    es = db.session.scalars(query).all()

    # db.session.close()


    return render_template("events.html", es=es, whatHappened=whatHappened)


@app.route('/kill-member/<mcfId>')
@admin_required
def kill_member(mcfId):
    
    
    stmt = sa.delete(Member).where(Member.mcfId == mcfId)
    db.session.execute(stmt)
    db.session.commit()

    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))


    query = sa.select(Member).where(Member.isAdmin == False)
    ms = db.session.scalars(query).all()

    # return "member successfully removed"
    # return render_template("members.html", ms=ms, whatHappened="Member successfully killed")
    return redirect(url_for("find_members", ms=ms, whatHappened="Member successfully killed"))

@app.route('/kill-members')
@admin_required
def kill_members():
    
    
    stmt = sa.delete(Member).where(Member.isAdmin == False)
    db.session.execute(stmt)
    db.session.commit()


    query = sa.select(Member).where(Member.isAdmin == False)
    ms = db.session.scalars(query).all()

    # return "member successfully removed"
    return redirect(url_for("find_members", ms=ms, whatHappened="All killed"))



@app.route('/events')
@admin_required
def find_events():
    


            

    es = None


    try:
        es = db.session.query(Event).all()
        eds = db.session.query(EventDeleted).all()
        es.extend(eds)

    except Exception as e:
        db.session.rollback()
        return f"An error occurred: {str(e)}", 500    

    # if not es:
    #     return render_template("events.html")
        

    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))


    # db.session.close()



    whatHappened = request.args.get("whatHappened")
    if not whatHappened:
        whatHappened = ""

    return render_template("events.html", es=es, whatHappened=whatHappened)



@app.route('/members')
@admin_required
def find_members():

    page = request.args.get("page", 1, type=int)
    whatHappened = ""
    if request.args.get("whatHappened"):
        whatHappened = request.args.get("whatHappened")
    
    
    query = sa.select(Member).where(Member.isAdmin == False).order_by(Member.mcfName)
    ms_paginate=db.paginate(query, page=page, per_page=20, error_out=False)
    # ms = db.session.scalars(query).all()

    # prev_url = "a_page/page=23"
    prev_url = url_for("find_members", page=ms_paginate.prev_num)
    next_url = url_for("find_members", page=ms_paginate.next_num)


    # https://stackoverflow.com/questions/14754994/why-is-sqlalchemy-count-much-slower-than-the-raw-query
    statement = db.session.query(db.func.count(Member.mcfId))
    count = db.session.scalars(statement).first() # coz I dont know a better/faster way to count records


    # db.session.close()
    
    # return "wait"
    # ms_dict = [m.__dict__ for m in ms]
    return render_template("members.html", ms=ms_paginate.items, prev_url=prev_url, next_url=next_url, page=page, totalPages=ms_paginate.pages, totalCount=count, whatHappened=whatHappened)



@app.route('/event-members/<id>')
@admin_required
def event_members(id):


    eventId = id

    statement = db.select(EventMember).where(EventMember.eventId == eventId)
    ems = db.session.scalars(statement).all()

    statement = db.select(Event).where(Event.id == eventId)
    e = db.session.scalars(statement).first()
    # endgeteventname

    
    # ===== trying something radical, list comprehension and in_() operator
    # ===== in_() works, but it relies on the __repr__(self) function, I dont like it
    list_of_mcfId = [em.mcfId for em in ems]
    # app.logger.info(list_of_mcfId)
    # app.logger.info(ms)

    ms = []

    for mcfId in list_of_mcfId:
        statement = db.select(Member).where(Member.mcfId == mcfId, Member.isAdmin == False)
        m = db.session.scalars(statement).first()
        ms.append(m)



    


    return render_template("event-members.html", ms=ms, eventName=e.tournamentName, eventId=eventId)
        


# ===== from: https://nrodrig1.medium.com/flask-mail-reset-password-with-token-8088119e015b
@app.route('/send-reset-email')
def send_reset_email():
    s=Serializer(app.config['SECRET_KEY'])
    
    # some_id, has no special meaning, mostly internal to TimedJSONWebSignatureSerializer/URLSafeTimedSerializer
    token = s.dumps({'some_id': current_user.mcfId}, salt="reset_pass")
    app.logger.info("=====")
    app.logger.info(f"token created: {token}")
    app.logger.info("=====")
    # token = user.get_reset_token()

    msg = Message('Password Reset Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[app.config["ADMIN_EMAIL"]])
    msg.body = f"""To reset your password follow this link:
    {url_for('reset_password', token=token, _external=True)}
    If you ignore this email no changes will be made
    """

    try:
        mail.send(msg)
        return redirect(url_for("main_page", whatHappened="Info: Password reset link successfully sent"))
    except Exception as e:
        return redirect(url_for("main_page", whatHappened=f"Error: {str(e)}"))

    return redirect()




def verify_reset_token(token):
    app.logger.info("=====")
    app.logger.info(f"verify_reset_token with token received: {token}")
    app.logger.info("=====")
    s=Serializer(app.config['SECRET_KEY'])
    app.logger.info("=====")
    app.logger.info(f"Serializer instance: {s}")
    app.logger.info("=====")
    try:
        some_id = s.loads(token, salt="reset_pass", max_age=int(app.config["TOKEN_MAX_AGE"]))['some_id']
        app.logger.info("=====")
        app.logger.info(f"some_id {some_id}")
        app.logger.info("=====")
    except:
        return None
    return Member.query.get(some_id)


# @app.route('/reset-password/<token>', methods=['GET','POST'])
# def reset_password(token):
@app.route('/reset-password', methods=['GET','POST'])
def reset_password():
    app.logger.info("=====")
    app.logger.info("reset_pasword")
    app.logger.info("=====")

    if request.method == 'GET':
        token = request.args.get("token")
        app.logger.info("=====")
        app.logger.info(f"token received: {token}")
        app.logger.info("=====")
        user = verify_reset_token(token)
        app.logger.info("=====")
        app.logger.info(f"user passed: {user}")
        app.logger.info("=====")
        if user is None:
            return redirect(url_for('main_page', whatHappened="Invalid token"))
        return render_template('reset-password.html', token=token)
    
    if request.method == 'POST':
        token = request.form["token"]
        user = verify_reset_token(token)
        user.set_password(password = request.form["newPassword"])
        # user.password = request.form["newPassword"]
        db.session.commit()
        return redirect(url_for("main_page", whatHappened="Info: Your password has been updated!"))


# dont delete this method, for our own documentation
@app.route('/send-email')
def send_mail():
    msg = Message(
        # ===== if we dont set sender it will use MAIL_DEFAULT_SENDER
        # sender=app.config['MAIL_USERNAME'],
        subject="hello i just got sent from Flask",
        recipients=["wan.ardie.mejia@gmail.com"],
        body="this is a test body"
    )

    try:
        mail.send(msg)
        return redirect(url_for("main_page", whatHappened="Info: Password reset link successfully sent"))
    except Exception as e:
        return redirect(url_for("main_page", whatHappened=f"Error: {str(e)}"))





@app.route('/upload-logs', methods = ["GET"])
@admin_required
def upload_logs():

    statement = db.select(File)
    fs = db.session.scalars(statement).all() # coz I dont know a better/faster way to count records
    whatHappened = ""
    if not fs:
        whatHappened = "Info: No entries yet"

    return render_template("upload-logs.html", fs=fs)


@app.route('/upload-logs-by-event/<int:id>', methods = ["GET"])
@admin_required
def upload_logs_by_event(id):

    
    eventId = id

    if request.args.get("whatHappened"):
        return render_template("upload-logs-by-event.html", whatHappened=request.args.get("whatHappened"))

    statement = db.select(File).where(File.eventId == eventId)
    fs = db.session.scalars(statement).all()
    whatHappened = ""
    if not fs:
        whatHappened = "Info: No entries yet"

    return render_template("upload-logs-by-event.html", fs=fs, whatHappened=whatHappened)




@app.route('/withdrawal-logs', methods = ["GET"])
@admin_required
def withdrawal_logs():

    statement = db.select(Withdrawal)
    ws = db.session.scalars(statement).all() # coz I dont know a better/faster way to count records
    whatHappened = ""
    if not ws:
        whatHappened = "Info: No entries yet"

    return render_template("withdrawal-logs.html", ws=ws)





@app.route('/withdrawal-logs-by-event/<int:id>', methods = ["GET"])
@admin_required
def withdrawal_logs_by_event(id):

    
    eventId = id

    if request.args.get("whatHappened"):
        return render_template("withdrawal-logs-by-event.html", whatHappened=request.args.get("whatHappened"))

    statement = db.select(Withdrawal).where(Withdrawal.eventId == eventId)
    ws = db.session.scalars(statement).all()
    whatHappened = ""
    if not ws:
        whatHappened = "Info: No entries yet"

    return render_template("withdrawal-logs-by-event.html", ws=ws, whatHappened=whatHappened)



@app.route('/kill-withdrawal-log-by-event', methods = ["POST"])
@admin_required
def kill_withdrawal_log_by_event():

    eventId = request.form["id"]



    statement = sa.delete(Withdrawal).where(Withdrawal.eventId == eventId)
    db.session.execute(statement)


    try:
        db.session.commit()
        whatHappened = "Logs emptied"
    except:
        db.session.rollback()
        whatHappened = "something went wrong"

    return redirect(url_for("withdrawal_logs_by_event", id=eventId, whatHappened=whatHappened))

@app.route('/kill-upload-log-by-event', methods = ["POST"])
@admin_required
def kill_upload_log_by_event():

    eventId = request.form["id"]



    statement = sa.delete(File).where(File.eventId == eventId)
    db.session.execute(statement)


    try:
        db.session.commit()
        whatHappened = "Logs emptied"
    except:
        db.session.rollback()
        whatHappened = "something went wrong"

    return redirect(url_for("upload_logs_by_event", id=eventId, whatHappened=whatHappened))








                    



@app.route('/')
@admin_required
def main_page():
    whatHappened = request.args.get('whatHappened')
    if not whatHappened:
        whatHappened = ""
    return render_template("main-page.html", whatHappened=whatHappened)


@app.route('/login', methods=['POST', 'GET'])   
def login():
    # logout_user()
    if current_user.is_authenticated:
        if current_user.isAdmin:
            return redirect(url_for('main_page'))
        else:
            return redirect(url_for('member_front'))
    if request.method == 'POST':

        csrf_token = request.form['csrf_token']
        app.logger.info("CSRF Token (Backend):", csrf_token)
    
        mcfId = request.form['mcfId']
        password = request.form['password']

        # app.logger.info('========== ---------- ++++++++++')
        # app.logger.info('Received data:', mcfId , password)
        # app.logger.info('========== ---------- ++++++++++')


        m = Member.query.filter_by(mcfId=mcfId).first()
        if m is None:
            return render_template("login.html", whatHappened = "Member does not exist")

        
        if not m.check_password(password):    
            # return C_templater.custom_render_template("Login Problem", ["Wrong password"], True)
            return render_template("login.html", whatHappened = "Ooops, wrong password")
        else:
            login_user(m)
            if current_user.isAdmin:
                return redirect(url_for('main_page'))
            else:
                return redirect(url_for('member_front'))
            

        # endpost
    else:
        whatHappened = request.args.get("whatHappened")
        # endget
        return render_template('login.html', whatHappened=whatHappened)




@app.errorhandler(BadRequest)
def handle_bad_request(e):
    if "The CSRF token is missing" in str(e) or "The CSRF token has expired" in str(e) :
        return redirect(url_for('login', whatHappened="Error: "+str(e)))
    
    # return "Bad Request",400
    return redirect(url_for('login', whatHappened="Error: "+str(e)))



@app.route('/form-submission', methods = ['POST'])
@login_required
def form_submission():
    whatHappened = ""
    mcfId = current_user.mcfId
    statement = db.select(Member).where(Member.mcfId == mcfId)
    m = db.session.scalars(statement).first()
    if m.isAdmin:
        return redirect(url_for('member_front', whatHappened="Info: admin ans not saved to avoid spoiling ans data"))

        
    # app.logger.info("==========")    
    # app.logger.info(dir(request.args) )    
    # app.logger.info(request.form.keys() )
    # app.logger.info(request.form.get("fullname") )
    # app.logger.info(request.form.listvalues())


    eventId = request.form['eventId']


    # deleteandbackupsubmission
    statement = db.select(FormQuestionAnswers).where(FormQuestionAnswers.mcfId == current_user.mcfId, FormQuestionAnswers.eventId == eventId)
    old_fqas = db.session.scalars(statement).all()

    old_answers = []
    for old_fqa in old_fqas:
        fqad = FormQuestionAnswersDeleted(
            mcfId=old_fqa.mcfId,
            fieldName=old_fqa.fieldName,
            eventId=old_fqa.eventId,
            answerString=old_fqa.answerString,
            subgroupId=old_fqa.subgroupId
        )

        old_answers.append(fqad)

    db.session.add_all(old_answers)

    statement = sa.delete(FormQuestionAnswers).where(FormQuestionAnswers.mcfId == current_user.mcfId, FormQuestionAnswers.eventId == eventId)
    db.session.execute(statement)
    try:
        db.session.commit()
        whatHappened = "answers successfully recorded"
    except IntegrityError as i:
        db.session.rollback()
        whatHappened=f"IntegrityError: {i}"
        return redirect(url_for('member_front', whatHappened=whatHappened))
    # enddeleteandbackupsubmission

    # for fieldname,answer in request.form.items():
    #     app.logger.info("======")
    #     app.logger.info(fieldname)
    #     app.logger.info(answer)
    #     app.logger.info("======")


    # endweirdtest
            
            
    answers = []
    for longFieldname,answer in request.form.items():
        isFile = None
        fieldname = longFieldname
        if fieldname == "eventId" or fieldname == "csrf_token":
            continue

        try:
            uploadedDocument = request.files[fieldname]
            isFile = True
        except:
            pass

        if "subgroup" in fieldname:
            ignore, subgroupId, fieldname = fieldname.split("::")
        else:
            subgroupId = None
        if "[]" in fieldname:
            checkboxList = request.form.getlist(longFieldname)
            # None values are custom, we remove None when users select checkbox values
            if len(checkboxList) > 1:
                checkboxList.remove("-")
            fqa = FormQuestionAnswers(
                mcfId=current_user.mcfId,
                fieldName=fieldname.split("[]")[0],
                eventId=eventId,
                answerString= ",".join(checkboxList),
                subgroupId=subgroupId
            )
            # endcheckboxsubmission
        elif isFile:
            fullfilePath = ""
            isSuccess, anyUpload, errorMsg, fullFilePath = upload_document(uploadedDocument, eventId, fieldname)
            if isSuccess:
                if anyUpload:
                    fqa = FormQuestionAnswers(
                        mcfId=current_user.mcfId,
                        fieldName=fieldname,
                        eventId=eventId,
                        answerString=fullFilePath,
                        subgroupId=subgroupId
                    )
                else:
                    fqa = FormQuestionAnswers(
                        mcfId=current_user.mcfId,
                        fieldName=fieldname,
                        eventId=eventId,
                        answerString="-",
                        subgroupId=subgroupId
                    )
            else:
                return redirect(url_for('member_front', whatHappened="Error: " + errorMsg))
                # endfilesubmission
        else:
            fqa = FormQuestionAnswers(
                mcfId=current_user.mcfId,
                fieldName=fieldname,
                eventId=eventId,
                answerString=answer,
                subgroupId=subgroupId
            )
            # endnormalsubmission



        answers.append(fqa)
            
    db.session.add_all(answers)
    
    try:
        db.session.commit()
        whatHappened = "answers successfully recorded"
    except IntegrityError as i:
        db.session.rollback()
        whatHappened=f"IntegrityError: {i}"
        return redirect(url_for('member_front', whatHappened=whatHappened))
        # endforloopanswers

        # return "nothing here"
    return redirect(url_for('member_front', whatHappened=whatHappened))

        
        


    # ===== Example of sample return expected
    # membersAnswers = {
    #     # the key is meaningless and unique, like a primary key in DB, stupid useless to humans but important
    #     "1234Q1 event": {
    #         "mcfId": "1233",
    #         "name": "Ardie",
    #         "gender": "M"
    #     },
    #     "5678Q1 event": {
    #         "mcfId": "1233",
    #         "name": "Hanifa",
    #         "gender": "F"
    #     }
    # }    
    
    # return render_template('form-question-answers.html', membersAnswers=membersAnswers, whatHappened=whatHappened)



@app.route('/event-answers-page', methods = ['POST'])
@admin_required
def event_answers_page():
    whatHappened = ""
    membersAnswers = {}

    eventId = request.form.get('eventId')


    statement = db.select(Event).where(Event.id == eventId)
    e = db.session.scalars(statement).first()
    app.logger.info(e)
    # endgeteventname
    
    
    # tablecolumns    
    statement = db.select(FormQuestionAnswers).where(FormQuestionAnswers.eventId == eventId)
    res_first = db.session.scalars(statement).first()
    if not res_first:
        return render_template('event-answers-page.html', membersAnswers={}, whatHappened="no entries yet", eventId=eventId, eventName=e.tournamentName)
        
    mcfId = res_first.mcfId
    

    statement = db.select(FormQuestionAnswers).where(FormQuestionAnswers.eventId == eventId, FormQuestionAnswers.mcfId == mcfId)
    single_mcfId_eventId = db.session.scalars(statement).all()
    

    membersAnswers["000000"] = {}


    membersAnswers["000000"]["mcfId"] = {"value": "", "subgroupId": None}
    for mcfId_eventId in single_mcfId_eventId:
        membersAnswers["000000"][mcfId_eventId.fieldName] = {"value": "", "subgroupId": mcfId_eventId.subgroupId}

    # endsubtablecolumns

    

    statement = db.select(FormQuestionAnswers).where(FormQuestionAnswers.eventId == eventId)
    fqas = db.session.scalars(statement).all()

    for fqa in fqas:
        unique_key = str(fqa.mcfId) + str(eventId)
        try:
            membersAnswers[unique_key]["mcfId"] = {
                "value": fqa.mcfId,
                "subgroupId": None
            }
            membersAnswers[unique_key][fqa.fieldName] = {"value": fqa.answerString, "subgroupId": fqa.subgroupId}

        except:
            membersAnswers[unique_key] = {}
            membersAnswers[unique_key]["mcfId"] = {
                "value": fqa.mcfId,
                "subgroupId": None
            }
            membersAnswers[unique_key][fqa.fieldName] = {"value": fqa.answerString, "subgroupId": fqa.subgroupId}





    # ===== Example of sample return expected
    #     # the key is meaningless and unique, like a primary key in DB, not used in the html, 00000 is meant for table column
    # membersAnswers = {
    #     "000000": {
    #         "mcfId": "1111",
    #         "name": "spiderman",
    #         "gender": "M",
    #          ...
    #     },
    #     "some_mcfIdSome_eventId": {
    #         "mcfId": "1112",
    #         "name": "Ardie",
    #         "gender": "M",
    #          ...
    #     },
    #     "some_mcfIdSome_eventId": {
    #         "mcfId": "1113",
    #         "name": "Hanifa",
    #         "gender": "F",
    #          ...
    #     }
    # }    

    app.logger.info(membersAnswers)
    return render_template('event-answers-page.html', membersAnswers=membersAnswers, eventId=eventId, eventName=e.tournamentName, whatHappened=whatHappened)


@app.route('/event-answers-page-overwritten', methods = ['POST'])
@admin_required
def event_answers_page_overwritten():
    whatHappened = ""
    membersAnswers = {}

    eventId = request.form.get('eventId')

    statement = db.select(Event).where(Event.id == eventId)
    e = db.session.scalars(statement).first()
    app.logger.info(e)
    # endgeteventname

    
    # tablecolumns    
    statement = db.select(FormQuestionAnswersDeleted).where(FormQuestionAnswersDeleted.eventId == eventId)
    res_first = db.session.scalars(statement).first()
    if not res_first:
        return render_template('event-answers-page-overwritten.html', membersAnswers={}, whatHappened="no entries yet", eventName=e.tournamentName, eventId=eventId)
        
    mcfId = res_first.mcfId
    

    statement = db.select(FormQuestionAnswersDeleted).where(FormQuestionAnswersDeleted.eventId == eventId, FormQuestionAnswersDeleted.mcfId == mcfId)
    single_mcfId_eventId = db.session.scalars(statement).all()
    

    membersAnswers["000000"] = {}


    
    membersAnswers["000000"]["mcfId"] = {"value": "", "subgroupId": None}
    for mcfId_eventId in single_mcfId_eventId:
        membersAnswers["000000"][mcfId_eventId.fieldName] = {"value": "", "subgroupId": mcfId_eventId.subgroupId}
        
    membersAnswers["000000"]["Deleted on"] = {"value": "", "subgroupId": None}





    # endsubtablecolumns

    

    statement = db.select(FormQuestionAnswersDeleted).where(FormQuestionAnswersDeleted.eventId == eventId)
    fqas = db.session.scalars(statement).all()

    for fqa in fqas:
        unique_key = str(fqa.mcfId) + str(eventId)

        try:
            membersAnswers[unique_key]["mcfId"] = {
                "value": fqa.mcfId,
                "subgroupId": None
            }
            membersAnswers[unique_key][fqa.fieldName] = {"value": fqa.answerString, "subgroupId": fqa.subgroupId}

        except:
            membersAnswers[unique_key] = {}
            membersAnswers[unique_key]["mcfId"] = fqa.mcfId
            membersAnswers[unique_key][fqa.fieldName] = {"value": fqa.answerString, "subgroupId": fqa.subgroupId}

            


    for fqa in fqas:
        unique_key = str(fqa.mcfId) + str(eventId)
        converted_time = fqa.deleted_at.astimezone(pytz.timezone('Asia/Kuala_Lumpur'))
        formatted_time = converted_time.strftime("%d/%m/%Y %H:%M")
        membersAnswers[unique_key]["Deleted on"] = {"value": formatted_time, "subgroupId": None}





    # ===== Example of sample return expected
    # membersAnswers = {
    #     # the key is meaningless and unique, like a primary key in DB, stupid useless to humans but important
    #     "some_mcfIdSome_eventId": {
    #         "mcfId": "1233",
    #         "name": "Ardie",
    #         "gender": "M",
    #          ...
    #     },
    #     "some_mcfIdSome_eventId": {
    #         "mcfId": "1233",
    #         "name": "Hanifa",
    #         "gender": "F",
    #          ...
    #     }
    # }    
    
    return render_template('event-answers-page-overwritten.html', membersAnswers=membersAnswers, eventId=eventId, eventName=e.tournamentName, whatHappened=whatHappened)


        
@app.route('/form-template', methods = ['GET'])
@login_required
def form_template():


    eventId = request.args.get("eventId")

    

    statement = db.select(FormQuestion).where(FormQuestion.eventId == eventId)
    frs = db.session.scalars(statement).all() # frs is form questions of an event
    if not frs:
        return redirect(url_for("member_front", whatHappened="Error: No form for this event yet"))


    # app.logger.info("==========")
    # app.logger.info(type(frs))
    # app.logger.info(type(frs[0]))
    # app.logger.info(frs)
    # app.logger.info(frs[0].to_dict())
    # app.logger.info("==========")

    frs_list = []
    # _elements = {}
    for fr in frs:
        frs_list.append(fr.to_dict())


    # the problem is our data is not unique
    # - hence we need to create a key from field+type
    # - so it becomes eg: nametext, genderdropdown, agetext, disabledradio
    # - for subgroupids, the leading question is saved first, before querying subgroup table
    # and then assigning it to a deeper dictionary
    
    a_dict = {}
    for fr_dict in frs_list:
        fieldtype_key = fr_dict["fieldName"]+fr_dict["type"]
        
        if fr_dict["subgroupId"]:


            a_dict[fieldtype_key] = {}
            a_dict[fieldtype_key]["value"] = [fr_dict["value"]]
            a_dict[fieldtype_key]["fieldName"] = fr_dict["fieldName"]
            a_dict[fieldtype_key]["type"] = fr_dict["type"]
            a_dict[fieldtype_key]["questionstring"] = fr_dict["questionstring"]
            a_dict[fieldtype_key]["subgroupId"] = fr_dict["subgroupId"]
            a_dict[fieldtype_key]["subgroup"] = {}
            # endsubgroupradio
            statement = db.select(FormQuestionSubgroup).where(FormQuestionSubgroup.subgroupId == fr_dict["subgroupId"])
            frsgs = db.session.scalars(statement).all()
            frsgs_list = []
            for frsg in frsgs:
                frsgs_list.append(frsg.to_dict())
            for frsg_dict in frsgs_list:
                subFieldtype_key = frsg_dict["fieldName"]+frsg_dict["type"]
                if frsg_dict["type"] == "dropdown" or frsg_dict["type"] == "checkbox" or frsg_dict["type"] == "radio":
                    # ===== becoz append is non-destructive, append logic always goes first
                    try:
                        a_dict[fieldtype_key]["subgroup"][subFieldtype_key]["value"].append(frsg_dict["value"])
                    except:
                        a_dict[fieldtype_key]["subgroup"][subFieldtype_key] = {}
                        a_dict[fieldtype_key]["subgroup"][subFieldtype_key]["value"] = [frsg_dict["value"]]
                        a_dict[fieldtype_key]["subgroup"][subFieldtype_key]["fieldName"] = frsg_dict["fieldName"]
                        a_dict[fieldtype_key]["subgroup"][subFieldtype_key]["type"] = frsg_dict["type"]
                        a_dict[fieldtype_key]["subgroup"][subFieldtype_key]["questionstring"] = frsg_dict["questionString"]
                        a_dict[fieldtype_key]["subgroup"][subFieldtype_key]["subgroupId"] = frsg_dict["subgroupId"]
                        # enddropdownorcheckbox_sub   
                else:
                    a_dict[fieldtype_key]["subgroup"][subFieldtype_key] = {
                        "fieldName": frsg_dict["fieldName"],
                        "type": frsg_dict["type"],
                        "questionstring": frsg_dict["questionString"],
                        "subgroupId": frsg_dict["subgroupId"]
                    }
                    # endtextorfile_sub
            

            

            #endsubgroup
        elif fr_dict["type"] == "dropdown" or fr_dict["type"] == "checkbox" or fr_dict["type"] == "radio":
            # ===== becoz append is non-destructive, append logic always goes first
            try:
                a_dict[fieldtype_key]["value"].append(fr_dict["value"])
            except:
                a_dict[fieldtype_key] = {}
                a_dict[fieldtype_key]["value"] = [fr_dict["value"]]
                a_dict[fieldtype_key]["fieldName"] = fr_dict["fieldName"]
                a_dict[fieldtype_key]["type"] = fr_dict["type"]
                a_dict[fieldtype_key]["questionstring"] = fr_dict["questionstring"]
                # enddropdownorcheckbox   
        else:
            a_dict[fieldtype_key] = {
                "fieldName": fr_dict["fieldName"],
                "type": fr_dict["type"],
                "questionstring": fr_dict["questionstring"]}
            # endtextorfile


    elements = list(a_dict.values())

        
    # ===== Example of return data expected, unique ID (fieldname + inputtype) is useless in template, only serves as organization
    # elements = {
    #     "genderdropdown" : {
    #         "value": ["M", "F", "Open"], "field": "gender", "type" : "text"
    #     },
    #     "fullicnametext" : {
    #         "value": "", "field": "fullname", "type" : "dropdown"
    #     },
    #     "disabledradio" : {
    #         "value": "Yes", "field": "disabled", "type" : "radio", "subgroupId" : "12345",
    #         "subgroup": {
    #             "genderdropdown" : {
    #                 "value": ["M", "F", "Open"], "field": "gender", "type" : "text"
    #             },
    #             "fullicnametext" : {
    #                 "value": "", "field": "fullname", "type" : "dropdown"
    #             }                
    #         }
    #     }
    # }
    
    return render_template("form-template.html", elements=elements, eventId=eventId)





# return render_template('event-form-subgroup-creator.html', whatHappened=whatHappened, eventId=eventId, subgroupId=subgroupId) 

# ===== there are no other ways get to event-form-subgroup-creator
@app.route('/event-form-subgroup-creator', methods = ['GET', 'POST'])
@admin_required
def event_form_subgroup_creator():
    if request.method == 'GET':
        whatHappened = request.args.get("whatHappened")
        if not whatHappened:
            whatHappened = ""
        eventId = request.args.get("eventId")
        subgroupId = request.args.get("subgroupId")
        #endget
        return render_template('event-form-subgroup-creator.html', whatHappened=whatHappened, eventId=eventId, subgroupId=subgroupId)
    else:
        whatHappened = ""
        eventId = request.form.get("eventId")
        subgroupId = request.form.get("subgroupId")

        if request.form.get("button") == "add":
            if request.form.get("type") == "dropdown" or request.form.get("type") == "checkbox" or request.form.get("type") == "radio":
                if request.form.get("field") == "" or request.form.get("questionstring") == "" or request.form.get("value") == "":
                    return redirect(url_for('event_form_subgroup_creator', whatHappened="Error: input fields cannot be empty", eventId=eventId, subgroupId=subgroupId))
                values = request.form.get("value").split("::")

                for value in values:
                    fqs = FormQuestionSubgroup(
                        subgroupId=subgroupId,
                        fieldName=request.form.get("field"),
                        eventId=eventId,
                        questionString=request.form.get("questionstring"),
                        value=value,
                        type=request.form.get("type")
                    )
                    try:
                        db.session.add(fqs)
                        db.session.commit()
                        whatHappened = request.form.get("field") + " - " + request.form.get("type") + " created"
                    except IntegrityError as i:
                        db.session.rollback()
                        whatHappened=f"IntegrityError: {i}"
                        return redirect(url_for('event_form_subgroup_creator', whatHappened=whatHappened, eventId=eventId, subgroupId=subgroupId))
                #enddropdownorrradio
                return redirect(url_for('event_form_subgroup_creator', whatHappened=whatHappened, eventId=eventId, subgroupId=subgroupId))
            elif request.form.get("type") == "text" or request.form.get("type") == "file":
                if request.form.get("field") == "" or request.form.get("questionstring") == "":
                    return redirect(url_for('event_form_subgroup_creator', whatHappened="Error: only values field can be empty", eventId=eventId, subgroupId=subgroupId))
                fqs = FormQuestionSubgroup(
                    subgroupId=subgroupId,
                    fieldName=request.form.get("field"),
                    eventId=eventId,
                    questionString=request.form.get("questionstring"),
                    value="",
                    type=request.form.get("type")
                )
                try:
                    db.session.add(fqs)
                    db.session.commit()
                    whatHappened = request.form.get("field") + " - " + request.form.get("type") + " created"
                except IntegrityError as i:
                    db.session.rollback()
                    whatHappened=f"IntegrityError: {i}"
                    return redirect(url_for('event_form_subgroup_creator', whatHappened=whatHappened, eventId=eventId, subgroupId=subgroupId))
                #endtextorfile                        
            #endaddbutton
            return redirect(url_for('event_form_subgroup_creator', whatHappened=whatHappened, eventId=eventId, subgroupId=subgroupId))
        
        if request.form.get("button") == "finishgroup":
            return redirect(url_for('event_form_creator', whatHappened="subgroup done", eventId=eventId))    

        
        #endpost

        
    


@app.route('/event-form-creator', methods = ['POST', 'GET'])
@admin_required
def event_form_creator():
    if request.method == 'GET': # ========== we need delete, or modify this, we never the GET for this API

        eventId = request.args.get('eventId')
        if not eventId:
            return render_template("main_page", whatHappened="something went wrong")
                
        whatHappened = request.args.get("whatHappened")
        if not whatHappened:
            whatHappened = ""

        # endget
        return render_template("event-form-creator.html", whatHappened=whatHappened, eventId=eventId)
    
    else:
        eventId = request.form.get("eventId")
        if request.form.get("button") == "start_create":
            tournamentName, whatHappened = kill_form_descendents_by_id(eventId)
            # endstartcreate
            return redirect(url_for('event_form_creator', whatHappened="Lets get started", eventId=eventId))
        elif request.form.get("button") == "add":
            if request.form.get("type") == "dropdown" or request.form.get("type") == "checkbox" or request.form.get("type") == "radio":
                if not request.form.get("value"):
                    return redirect(url_for('event_form_creator', whatHappened="Error: value must not be empty", eventId=eventId))
                values = request.form.get("value").split("::")
                for value in values:
                    fr = FormQuestion(eventId=eventId,
                                      fieldName=request.form.get("field"),
                                      value=value,
                                      questionstring=request.form.get("questionstring"),
                                      type=request.form.get("type")
                                      )
                    try:
                        db.session.add(fr)
                        db.session.commit()
                        whatHappened = request.form.get("field") + " - " + request.form.get("type") + " created"
                    except IntegrityError as i:
                        db.session.rollback()
                        whatHappened=f"IntegrityError: {i}"
                        return redirect(url_for('event_form_creator', whatHappened=whatHappened, eventId=eventId))
                #enddropdownorcheckboxorradio
                return redirect(url_for('event_form_creator', whatHappened=whatHappened, eventId=eventId))
            else:
                if not request.form.get("value"):
                    return redirect(url_for('event_form_creator', whatHappened="Error: value must not be empty", eventId=eventId))
                fr = FormQuestion(eventId=eventId,
                                   fieldName=request.form.get("field"),
                                   value="",
                                   questionstring=request.form.get("questionstring"),
                                   type=request.form.get("type")
                                   )
                try:
                    db.session.add(fr)
                    db.session.commit()
                    whatHappened = request.form.get("field") + " - " + request.form.get("type") + " created"
                except IntegrityError as i:
                    db.session.rollback()
                    whatHappened=f"IntegrityError: {i}"
                    return redirect(url_for('event_form_creator', whatHappened=whatHappened, eventId=eventId))
                # endtextorfile
                #endadd
                return render_template("event-form-creator.html", whatHappened=whatHappened, eventId=eventId)
        elif request.form.get("button") == "subgroup":
            whatHappened = ""

            subgroupName = request.form.get("subgroupName")
            if not subgroupName:
                return redirect(url_for('event_form_creator', whatHappened="Error: subgroup name must not be empty", eventId=eventId))

                            
            
            subgroupId=uuid.uuid4()
            fq = FormQuestion(eventId=eventId,
                              fieldName=request.form.get("field"),
                              value="Yes",
                              questionstring=request.form.get("questionstring"),
                              type=request.form.get("type"),
                              subgroupId=subgroupId,
                              subgroupName=request.form.get("subgroupName"),
                              )

            try:
                db.session.add(fq)
                db.session.commit()
            except IntegrityError as i:
                db.session.rollback()
                whatHappened=f"IntegrityError: {i}"
                return redirect(url_for('event_form_creator', whatHappened=whatHappened, eventId=eventId))

            
            #endsubgroup
            return redirect(url_for ('event_form_subgroup_creator', whatHappened="new subgroup", eventId=eventId, subgroupId=subgroupId))
        

            
        else:
            if request.form.get("button") == "done":
                if request.form.get("whatHappened") == "Lets get started":
                    return redirect(url_for('find_events', whatHappened="No Form Created"))
                
            form_vars = ""

            # enddone
            return redirect(url_for('find_events', whatHappened="Form creation loop done"))
        # endpost

        
def kill_form_descendents_by_id(eventId):

    whatHappened = ""
    statement = sa.select(Event).where(Event.id == eventId)
    e = db.session.scalars(statement).first()
    if not e:
        return None, "there are no form descendents to kill"
    tournamentName = e.tournamentName

    statement = sa.delete(FormQuestion).where(FormQuestion.eventId == eventId)
    db.session.execute(statement)
    
    # try:
    #     db.session.commit()
    # except:
    #     db.session.rollback()
    #     return None, "something went wrong"

    statement = sa.delete(FormQuestionAnswers).where(FormQuestionAnswers.eventId == eventId)
    db.session.execute(statement)
    
    # try:
    #     db.session.commit()
    # except:
    #     db.session.rollback()
    #     return None, "something went wrong"

    
    statement = sa.delete(FormQuestionSubgroup).where(FormQuestionSubgroup.eventId == eventId)
    db.session.execute(statement)
    
    # try:
    #     db.session.commit()
    # except:
    #     db.session.rollback()
    #     return None, "something went wrong"

    statement = sa.delete(FormQuestionAnswersDeleted).where(FormQuestionAnswersDeleted.eventId == eventId)
    db.session.execute(statement)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return None, "something went wrong"


    return tournamentName, whatHappened

    
@app.route('/kill-form-descendents', methods = ["POST"])
@admin_required
def kill_form_descendents():
    
    whatHappened = ""
    eventId = request.form.get('eventId')
    if not eventId:
        eventId = request.args.get('eventId')


    tournamentName, whatHappened = kill_form_descendents_by_id(eventId)
    if tournamentName:
        whatHappened="All derived form data of " + tournamentName + " killed"

    return redirect(url_for('find_events', whatHappened=whatHappened))

    
    
    

    
    
@app.route('/member-front', methods=['GET', 'POST'])
@login_required
def member_front():
    if current_user.is_authenticated:
        if request.method == 'GET':
            trlists = []
            paymentProofs = []
            m = Member.query.filter_by(mcfId=current_user.mcfId).first()
            
            statement = db.select(EventDeleted)
            eds = db.session.scalars(statement).all()
            
            query = sa.select(Event)
            es = db.session.scalars(query).all()
            es.extend(eds)

            updatedTournamentId = request.args.get("updatedTournamentId")
            whatHappened = request.args.get("whatHappened")
            if updatedTournamentId:
                statement = db.select(Event).where(Event.id == updatedTournamentId)
                e = db.session.scalars(statement).first()
                whatHappened = whatHappened + e.tournamentName

            statement = db.select(EventMember).where(EventMember.mcfId == current_user.mcfId)
            ems = db.session.scalars(statement).all()


            if ems:
                for em in ems:
                    statement = db.select(Event).where(Event.id == em.eventId)
                    e = db.session.scalars(statement).first()
                    trlists.append(e)
            

                    # trlists.append(e.tournamentName)

            statement = db.select(File).where(File.mcfId == current_user.mcfId)
            fs = db.session.scalars(statement).all()


                
            if not whatHappened:
                whatHappened = ""



            # endget
            return render_template("member-front.html", m=m, tournamentRegistered=trlists, tournamentOptions=es, whatHappened=whatHappened, paymentProofs=fs)
        else:
            # app.logger.info("==========")
            # app.logger.info(request.form.get("mcfId"))
            # app.logger.info(request.form)
            # app.logger.info(request.form.get("button"))
            # app.logger.info("==========")

            
            whatHappened=""
            if request.form.get("button") == "save":
                updatedTournamentId = request.form["tournament_name"]
                # overwrite only if event non existing in m.events

                statement = db.select(EventDeleted).where(EventDeleted.id == updatedTournamentId)
                ed = db.session.scalars(statement).first()


                if ed:                
                    whatHappened = "Error: This event registration is already closed"
        
                    return redirect(url_for('member_front', whatHappened=whatHappened))

                statement = db.select(EventMember).where(EventMember.mcfId == current_user.mcfId, EventMember.eventId == updatedTournamentId)
                res = db.session.execute(statement).first()
                # app.logger.info("eeeeeeee")
                # app.logger.info(request.form["tournament_name"])
                if not res:
                    em = EventMember(mcfId=current_user.mcfId, eventId=updatedTournamentId)
                    db.session.add(em)
                try:
                    db.session.commit()
                    whatHappened="Saved: "
                except IntegrityError as i: 
                    db.session.rollback()
                    whatHappened=f"IntegrityError: {i}"

                    
                    # endsavebutton
            # elif request.form.get("button") == "withdraw":
            elif "withdraw" in request.form.get("button"):
                updatedTournamentId = request.form.get("button").split("_")[1]


                

                # return redirect(url_for('member_front', whatHappened="just a test", paymentProofs=""))

                # em = EventMember(mcfId=current_user.mcfId, eventId=request.form["tournament_name"])
                statement = sa.delete(EventMember).where(EventMember.mcfId == current_user.mcfId, EventMember.eventId == updatedTournamentId)
                db.session.execute(statement)
                #endkilleventmemberrel

                
                statement = db.select(Member).where(Member.mcfId == current_user.mcfId)
                m = db.session.scalars(statement).first()
                statement = db.select(Event).where(Event.id == updatedTournamentId)
                e = db.session.scalars(statement).first()
                w = Withdrawal(mcfId=current_user.mcfId, mcfName=m.mcfName, email=m.email, eventId=updatedTournamentId, tournamentName=e.tournamentName)
                db.session.add(w)
                #endwithdrawlog
                
                whatHappened = "Successully withdrawn from "

                try:
                    db.session.commit()
                except IntegrityError as i:
                    db.session.rollback()
                    whatHappened=f"IntegrityError: {i}"



                
                # endwithdrawbutton
            elif "fillForm" in request.form.get("button"):
                updatedTournamentId = request.form.get("button").split("_")[1]


                
                # endfillform
                return redirect(url_for('form_template', eventId=updatedTournamentId))


                



    


            # db.session.close()

            # endpost
            return redirect(url_for('member_front', whatHappened=whatHappened, updatedTournamentId=updatedTournamentId ))

    else:
        # endnotauthenticated
        return render_template("login.html")
        




def upload_document(uploadFile, eventId, fieldname):
    # paymentProofs = []
    # uploadFile = request.files['uploadFile']
    # if uploadFile.filename == '':
    #     # endemptycheck
    #     return redirect(url_for('member_front', whatHappened="Error: There is no file uploaded", updatedTournamentId="", paymentProofs=paymentProofs))

    isSuccess = True
    anyUpload = True
    

    if not uploadFile:
        isSuccess = True
        anyUpload = False
        return isSuccess, anyUpload, "File upload failed due to wrong filetype or something else", ""        
    if allowed_user_upload(uploadFile):
        filename = secure_filename(uploadFile.filename)
        fname, ext = os.path.splitext(uploadFile.filename)
        # disk_path = ""  # Path to the persistent disk
        # folder_name = "my_folder"
        # folder_path = os.path.join(disk_path, folder_name)
        statement = db.select(Event).where(Event.id == eventId)
        e = db.session.scalars(statement).first()
        
        eventName = "_".join(e.tournamentName.split())
        fieldname = "_".join(fieldname.split())
        mcfIdString = str(current_user.mcfId)
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], eventName, mcfIdString)

        try:
            os.makedirs(folder_path, exist_ok=True)
            # print(f"Folder '{folder_name}' created successfully at '{folder_path}'.")
        except Exception as e:
            
            return False, "something went wrong", ""
            # return redirect(url_for('member_front', whatHappened="Error: Something went wrong. Please contact web admin"))



        # ===== use os.path.join with care, it interprets slashes, and inserts its own, and can hide errors
        base_filename = fieldname + "_" + str(datetime.datetime.now().strftime("%Y-%m-%d__%H%M%S"))  + ext
        uploadFile.save(os.path.join(folder_path, base_filename))

        f = File(originalFilename=uploadFile.filename,
                 filename=base_filename,
                 filepath=folder_path,
                 mcfId=current_user.mcfId,
                 eventId=eventId
                 )
    
        try:
            db.session.add(f)
            db.session.commit()
        except IntegrityError as i:
            db.session.rollback()
            # endfileuploaderror
            return False, "error in attempting to log file uplaod in DB", ""


        

        isSuccess = True
        anyUpload = True
        
        # endfileupload
        return isSuccess, anyUpload, "", os.path.join(folder_path, base_filename)
    else:
        isSuccess = False
        anyUpload = False
        return isSuccess, anyUpload, "File upload failed due to wrong filetype or something else", ""
        



    

    


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))


@app.route('/bulk-upload-events-csv')
@admin_required
def bulk_upload_events_csv():
    # ========== we upload CSV using the kinda cool declarative_base, might not be good practice for readability
    with open(r'./input/event.csv', newline='') as csvfile:
        dictreader = csv.DictReader(csvfile, delimiter=',')
        for row in dictreader:            
            e = Event(tournamentName=row['tournamentName'], startDate=row['startDate'], endDate=row['endDate'], discipline=row['discipline'])
            db.session.add(e)

            # ===== try uploading bulk    
            try:
                db.session.commit()
            except IntegrityError as i:
                db.session.rollback()
                whatHappened=f"IntegrityError: {i}"
                return render_template("main-page.html", whatHappened=whatHappened)


    # return C_templater.custom_render_template("Successfull bulk upload", "event data", False)
# return redirect('/events')
    return render_template("main-page.html", whatHappened="Upload successfull and no duplicate or other issues")





@app.route('/bulk_upload_members_csv')
@admin_required
def bulk_upload_members_csv():


    # ========== we upload CSV using the kinda cool declarative_base, might not be good practice for readability
    duplicatesList= []
    filename="member.csv"
    mapFrom = C_mapper.excelToDatabase[filename]
    with open(r'./input/'+filename, newline='') as csvfile:
        dictreader = csv.DictReader(csvfile, delimiter=',')
        for row in dictreader:

            m = Member(mcfId=row[mapFrom['mcfId']], mcfName=row[mapFrom['mcfName']], gender=row[mapFrom['gender']], yearOfBirth=row[mapFrom['yearOfBirth']], state=row[mapFrom['state']], nationalRating=row[mapFrom['nationalRating']])
            m.set_password(row[mapFrom['password']])
            
            if not m.doesUserExist(m.mcfId):
                db.session.add(m)
            else:
                duplicatesList.append(m)


        # ===== try uploading bulk    
        try:
            db.session.commit()

        except IntegrityError as i:
            db.session.rollback()
            whatHappened=f"IntegrityError: {i}"
            return render_template("main-page.html", whatHappened=whatHappened)
        

        if not duplicatesList:            
            whatHappened = "Upload successful with no duplicates"
        else:
            whatHappened = "Upload successful with some duplicates"




    return render_template("main-page.html", whatHappened=whatHappened, whyHappened=duplicatesList)



@app.route('/bulk_upload_fide_csv')
@admin_required
def bulk_upload_fide_csv():
    # ========== we upload CSV using the kinda cool declarative_base, might not be good practice for readability

    duplicatesList= []
    filename="fide.csv"
    mapFrom = C_mapper.excelToDatabase[filename]
    with open(r'./input/'+filename, newline='') as csvfile:
        dictreader = csv.DictReader(csvfile, delimiter=',')
        for row in dictreader:




            statement = db.select(Member).where(Member.mcfId == row[mapFrom['mcfId']])
            m = db.session.scalars(statement).first()
            
            # (Member).where(mcfid == row['mcfId'])
            m.fideId = row[mapFrom['fideId']]
            m.fideName = row[mapFrom['fideName']]
            m.fideRating = row[mapFrom['fideRating']]
                
            # if m.doesUserExist(m.mcfId):
            #     duplicatesList.append(m)
            #     continue
            # db.session.add(m)
        # ===== try uploading bulk    
        try:
            db.session.commit()
        except IntegrityError as i:
            whatHappened=f"IntegrityError: {i}"
            return render_template("main-page.html", whatHappened="")
        
            # query = sa.select(Member).where(Member.mcfId == row[''])
            # f = db.session.scalar(query)
            # m.fide = f                           


        try:
            db.session.commit()
        except IntegrityError as i:
            db.session.rollback()
            whatHappened=f"IntegrityError: {i}"
            return render_template("main-page.html", whatHappened=whatHappened)

    # if not duplicatesList:            
    #     whatHappened = "Upload successful with no duplicates"
    # else:
    #     whatHappened = "Upload successful with some duplicates"

    return render_template("main-page.html", whatHappened="", whyHappened=[])



def processMcfList():
    filename="mcf.csv"


    mapFrom = C_mapper.excelToDatabase[filename]

    wanted_columns = [mapFrom['mcfId'], mapFrom['mcfName'], mapFrom['gender'], mapFrom['yearOfBirth'], mapFrom['state'], mapFrom['nationalRating'], mapFrom['fideId']]

    chunksize = 200
    fullfilename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(fullfilename, usecols=wanted_columns, chunksize=chunksize, dtype=str)


    skippedList = []
    newList = []
    values=[]
    
    for chunk in df:
        # app.logger.info("==========")
        # app.logger.info(type(chunk))
        # app.logger.info(chunk)
        # app.logger.info("==========")
        
        for index, row in chunk.iterrows():

            if Member.doesUserExist(row[mapFrom['mcfId']]):
                skippedList.append({"mcfId": row[mapFrom['mcfId']]})
                continue


            # app.logger.info("%%%%%")
            
            # app.logger.info(                
            # row[mapFrom['yearOfBirth']]
            # )
            # app.logger.info(
            #     convert_nan_to_string(
            #         row[mapFrom['yearOfBirth']]
            #     )
            # )
            # app.logger.info("%%%%%")

            # yearOfBirth = convert_nan_to_string(row[mapFrom['yearOfBirth']])
            dictMemberBeforeSaving = validate_before_saving(
                mcfName = row[mapFrom['mcfName']],
                yearOfBirth = row[mapFrom['yearOfBirth']],
                state = row[mapFrom['state']]
            )

            if not dictMemberBeforeSaving:
                skippedList.append({"mcfId": row[mapFrom['mcfId']]})
                continue
                
                
            values.append(
                {
                    "mcfId": row[mapFrom['mcfId']],
                    "mcfName": row[mapFrom['mcfName']],
                    "gender": row[mapFrom['gender']],
                    "yearOfBirth": dictMemberBeforeSaving["yearOfBirth"],
                    "state": row[mapFrom['state']],
                    "nationalRating": row[mapFrom['nationalRating']],
                    "events": "",
                    "fideId": Member.empty_string_to_zero(num = str(row[mapFrom['fideId']])),
                    "password": bcrypt.generate_password_hash(row[mapFrom['mcfId']].strip() \
                                                              + dictMemberBeforeSaving["yearOfBirth"].strip() \
                                                              ).decode('utf-8')
                }
            )
            newList.append({"mcfId": row[mapFrom['mcfId']]})

            # app.logger.info("==========")
            # app.logger.info(values)
            # app.logger.info("==========")
            

    if values:
        try:
            statement = db.insert(Member)
            db.session.execute(statement, values)
            db.session.commit()
            
        except IntegrityError as i:
            db.session.rollback()
            # app.logger.info(i._message())
            # return C_templater.custom_render_template("Data entry error", i._message(), False)
            # return redirect(url_for("main"))
            # return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)
            return f"IntegrityError: {i}", [], []


    if not skippedList:            
        whatHappened = "No records skipped"
    else:
        whatHappened = "Some skipped records"

    fullfilename = os.path.join(app.config['UPLOAD_FOLDER'], "mcf.csv")
    tryRemoveMcfFile(fullfilename)                


    return whatHappened, skippedList, newList



   

def processFrlList():
    filename = "frl.csv"
    skippedList = []
    whatHappened = ""
    updatesList = []

    mapFrom = C_mapper.excelToDatabase[filename]
    with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), newline='') as csvfile:
        dictreader = csv.DictReader(csvfile, delimiter=',')
        for row in dictreader:


            statement = db.select(Member).where(Member.fideId == row[mapFrom['fideId']])
            m = db.session.scalars(statement).first()
            if m:                          
                m.fideId=row[mapFrom['fideId']]
                m.fideName=row[mapFrom['fideName']]                       
                m.fideRating=row[mapFrom['fideRating']]
                updatesList.append(row[mapFrom["fideId"]])
            else:
                # whyHappened.append({
                #     "fideId": row[mapFrom['fideId']],
                #     "fideName": row[mapFrom['fideName']],
                #     "fideRating": row[mapFrom['fideRating']]
                #                     })
                skippedList.append(row[mapFrom["fideId"]])

        # ===== try uploading bulk    
    try:
        db.session.commit()

    except IntegrityError as i:
        db.session.rollback()
        whatHappened = f"IntegrityError: {i}"


    if not whatHappened and not skippedList:
        whatHappened = "PERFECT upload"
    elif not whatHappened and skippedList:
        whatHappened = "Successful upload with details below"


    tryRemoveMcfFile(os.path.join(app.config['UPLOAD_FOLDER'], "frl.csv"))


    return whatHappened, skippedList, updatesList




def updateMcfList():
    filename="mcf.csv"


    mapFrom = C_mapper.excelToDatabase[filename]
    
    wanted_columns = [mapFrom['mcfId'], mapFrom['mcfName'], mapFrom['gender'], mapFrom['yearOfBirth'], mapFrom['state'], mapFrom['nationalRating'], mapFrom['fideId']]


    try:
        fullfilename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        df = pd.read_csv(fullfilename, usecols=wanted_columns, dtype=str)
    except FileNotFoundError as f:
        return redirect(url_for('main_page', whatHappened="Error: File Not Found, Upload again" ))
        
        





    
    updatesList = []
    failedUpdatesList = []
    # ========== right now skippedList stores ID, which means we can be flexible on how to use it later for more feedback
    skippedList = []
    for index,row in df.iterrows():
        # app.logger.info(type(chunk))
        # app.logger.info(chunk)
        values=[]
        

        m = Member.query.filter_by(mcfId=row[mapFrom['mcfId']]).first()



            
        if m:
            dictMemberBeforeSaving = validate_before_saving(
                mcfName = row[mapFrom['mcfName']],
                yearOfBirth = row[mapFrom['yearOfBirth']],
                state = row[mapFrom['state']])
            if dictMemberBeforeSaving:            
                m.mcfName = dictMemberBeforeSaving["mcfName"]
                m.gender = row[mapFrom['gender']]
                m.yearOfBirth = dictMemberBeforeSaving["yearOfBirth"]
                m.state = row[mapFrom['state']]
                m.nationalRating = row[mapFrom['nationalRating']]
                m.fideId = row[mapFrom['fideId']]
                m.password = bcrypt.generate_password_hash(row[mapFrom['mcfId']].strip() \
                                                           + dictMemberBeforeSaving["yearOfBirth"].strip() \
                                                           ).decode('utf-8')
            
                updatesList.append(row[mapFrom['mcfId']])
            else:
                skippedList.append(row[mapFrom['mcfId']])


        else:
            skippedList.append(row[mapFrom['mcfId']])
                                

                               

            
        


                
        try:
            db.session.commit()
        except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
            # whatHappened = "DB-API IntegrityError"
            failedUpdatesList.append(row[mapFrom['mcfId']])
            db.session.rollback()
            # return C_templater.custom_render_template(errorTopic="DB-API IntegrityError", errorsList=[i._message], isTemplate=True)
        except DataError as d:
            failedUpdatesList.append(row[mapFrom['mcfId']])
            db.session.rollback()
            # return C_templater.custom_render_template(errorTopic="DB API DataError", errorsList=[d._message], isTemplate=True)


    if not updatesList and not failedUpdatesList:            
        whatHappened = "No updated records"
    if not updatesList and failedUpdatesList:            
        whatHappened = "No updated records with failed update details below"
    else:
        whatHappened = "Updated record details below"


    tryRemoveMcfFile(os.path.join(app.config['UPLOAD_FOLDER'], "mcf.csv"))                
                


    return whatHappened, updatesList, failedUpdatesList, skippedList



def updateFrlList():
    return "mpthing", "nptin"



@app.route('/bulk-process-all-mcf')
@admin_required
def bulk_process_all_mcf():


    if isFileUploaded("mcf.csv"):
        if isFileOversized("mcf.csv"):
            # whatHappened, updatesList, failedUpdatesList, skippedList = "Error: File is too large (> 500)", [], [], []
            return render_template("main-page.html", whatHappened="Error: File is too large (> 500)")
        else:        
            # whatHappened, updatesList, failedUpdatesList, skippedList = updateMcfList()
            whatHappened, skippedList, newList = processMcfList()
    else:
        return render_template("main-page.html", whatHappened="Error: File Not Found, Upload again")

    # return render_template("main-page.html", whatHappened=whatHappened, updatesList=updatesList, failedUpdatesList=failedUpdatesList, skippedList=skippedList)


    # fileOversized = isFileOversized("mcf.csv")



    return render_template("main-page.html", whatHappened=whatHappened, skippedList=skippedList, newList=newList)


@app.route('/bulk-process-all-frl')
@admin_required
def bulk_process_all_frl():
    if isFileUploaded("frl.csv"):
        if isFileOversized("frl.csv"):
            # whatHappened, updatesList, failed
            return render_template("main-page.html", whatHappened="Error: File is too large (> 500)")
        else:        
            # whatHappened, updatesList, failedUpdatesList, skippedList = updateMcfList()
            whatHappened, skippedList, updatesList = processFrlList()
    else:
        return render_template("main-page.html",
	whatHappened="Error: File Not Found, Upload again")
    


    return render_template("main-page.html", whatHappened=whatHappened, skippedList=skippedList, updatesList=updatesList)


@app.route('/bulk-update-all-mcf')
@admin_required
def bulk_update_all_mcf():
    # if not os.path.isfile("./storage/mcf.csv"):
    #     return C_templater.custom_render_template(errorTopic="Invalid Upload Name", errorsList=["files must be a csv and contain \"mcf\" in its filename"], isTemplate=True)
    # ===== failedUpdatesList: for now only the length of the list is used in the template

    if isFileUploaded("mcf.csv"):
        if isFileOversized("mcf.csv"):
            # whatHappened, updatesList, failedUpdatesList, skippedList = "Error: File is too large (> 500)", [], [], []
            return render_template("main-page.html", whatHappened="Error: File is too large (> 500)")
        else:        
            whatHappened, updatesList, failedUpdatesList, skippedList = updateMcfList()
    else:
        return render_template("main-page.html", whatHappened="Error: File Not Found, Upload again")

    return render_template("main-page.html", whatHappened=whatHappened, updatesList=updatesList, failedUpdatesList=failedUpdatesList, skippedList=skippedList)







def allowed_user_upload(uploadedDocument):
    mimetype = filetype.guess(uploadedDocument)
    filename = uploadedDocument.filename
    app.logger.info("+++++++")
    app.logger.info("+++++++")
    app.logger.info(
        'png' in mimetype.mime or 'pdf' in mimetype.mime or 'jpg' in mimetype.mime or 'jpeg' in mimetype.mime
    )
    app.logger.info("png" in mimetype.mime)

    app.logger.info("+++++++")

    isMimeAllowed = 'png' in mimetype.mime or 'pdf' in mimetype.mime or 'jpg' in mimetype.mime or 'jpeg' in mimetype.mime
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS'] and \
           isMimeAllowed

def allowed_bulk_mcf_upload(filename):
    # return True
    return "mcf" in filename.lower()
    # return '.' in filename and \
    #        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_bulk_frl_upload(filename):
    # return True
    return "frl" in filename.lower()
    # return '.' in filename and \
    #        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    

@app.route('/bulk-upload-all-files-mcf', methods=['POST'])
@admin_required
def bulk_upload_all_files_mcf():


        
    file1 = request.files['file1']


    if file1.filename == '':
        return render_template("main-page.html", whatHappened="There is no file uploaded", whyHappened=[])


    if file1 \
       and allowed_bulk_mcf_upload(file1.filename):
        filename1 = secure_filename(file1.filename)
        file1.save(os.path.join(app.config['UPLOAD_FOLDER'], 'mcf.csv'))
        return render_template("main-page.html", whatHappened="MCF file successfully uploaded")
    else:
        whatHappened = "CSV filename must contain mcf.   Eg: mcf-Q1.csv"
        return redirect(url_for('main_page', whatHappened=whatHappened))



    
@app.route('/bulk-upload-all-files-frl', methods=['POST'])
@admin_required
def bulk_upload_all_files_frl():
        
    file2 = request.files['file2']

    if file2.filename == '':
        return render_template("main-page.html", whatHappened="There is no file uploaded")



    if file2 \
       and allowed_bulk_frl_upload(file2.filename):
        filename2 = secure_filename(file2.filename)
        file2.save(os.path.join(app.config['UPLOAD_FOLDER'], 'frl.csv'))
        # return 'File successfully uploaded'
        return render_template("main-page.html", whatHappened="FRL file successfully uploaded")
    else:
        whatHappened = "CSV filename must contain frl.   Eg: my-frl-Q4.csv"
        return redirect(url_for('main_page', whatHappened=whatHappened))


@app.route('/partial-download', methods = ["POST"])
@admin_required
def partial_download():
    
    downloadOffset = request.args.get("downloadOffset", type=int)

    query = sa.select(Member).where(Member.isAdmin == False).order_by(Member.mcfName)
    ms_paginate=db.paginate(query, page=downloadOffset, per_page=500, error_out=False)
    app.logger.info(ms_paginate)
    app.logger.info(ms_paginate)
    app.logger.info(ms_paginate.items)
    if not ms_paginate.items:
        return redirect(url_for("find_members", whatHappened = "no Members to download"))


    var1 = ms_paginate.items[0]
    # app.logger.info(var1.events)
    
    df = pd.DataFrame()
    rec = []
    for m in ms_paginate.items:
        rec.append(m.as_dict_for_file("mcf.csv"))
        # rec.append(m.as_dict())
        
    df = df.from_dict(rec)

    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(output, download_name="Download" + str(datetime.date.today()) + "_Partial" + str(downloadOffset) + ".csv", as_attachment=True, mimetype="str") # not sure if mimetype is necessary, can try removing



@app.route('/an-evt-ans-download')
@admin_required
def an_evt_ans_download():


    # query = sa.select(Member).order_by(Member.mcfName)

    whatHappened = ""
    # ===== OrderDict is part of Python already, if you remember what you read in EloquentPython
    # membersAnswers = {}
    membersAnswers = {}

    eventId = request.args['eventId']


    


    statement = db.select(Event).where(Event.id == eventId)
    e = db.session.scalars(statement).first()
    eventName = "_".join(e.tournamentName .split(" "))    

    

    statement = db.select(FormQuestionAnswers).where(FormQuestionAnswers.eventId == eventId)
    fqas = db.session.scalars(statement).all()

    for fqa in fqas:
        unique_key = str(fqa.mcfId) + str(eventId)
        try:
            membersAnswers[unique_key]["mcfId"] = fqa.mcfId
                # "subgroupId": None

            membersAnswers[unique_key][fqa.fieldName] = fqa.answerString
                                                         # "subgroupId": fqa.subgroupId


        except:
            membersAnswers[unique_key] = {}
            membersAnswers[unique_key]["mcfId"] = fqa.mcfId
            membersAnswers[unique_key][fqa.fieldName] = fqa.answerString

    key_1st = next(iter(membersAnswers))
    correct_columns = list(membersAnswers[key_1st])


    # ===== Example of sample return expected
    # membersAnswers = {
    #     # the key is meaningless and unique, like a primary key in DB, stupid useless to humans but important
    #     "some_mcfIdSome_eventId": {
    #         "mcfId": "1233",
    #         "name": "Ardie",
    #         "gender": "M"
    #     },
    #     "some_mcfIdSome_eventId": {
    #         "mcfId": "1233",
    #         "name": "Hanifa",
    #         "gender": "F"
    #     }
    # }
    
    # df = pd.DataFrame(membersAnswers)
    df = pd.DataFrame(membersAnswers)

    output = BytesIO()
    # ===== basically reordering internal or 2nd dimension, not the most readable one liner
    df.transpose()[correct_columns].to_csv(output, index=False)
    # df.transpose().to_csv(output, index=False)
    output.seek(0)
    

    # return "nothing"
    
    # not sure if mimetype is necessary, can try removing
    # return "nothing burger"
    return send_file(output, download_name=
                     "Download" +
                     str(datetime.date.today()) +
                     # "_Partial" +
                     # str(downloadOffset) +
                     "_" +
                     eventName +
                     ".csv",
                     as_attachment=True, mimetype="str")




@app.route('/an-evt-mmbrs-download')
@admin_required
def an_evt_mmbrs_download():


    whatHappened = ""
    eventMembers = {}

    eventId = request.args['eventId']


    statement = db.select(EventMember).where(EventMember.eventId == eventId)
    ems = db.session.scalars(statement).all()

    list_of_mcfId = [em.mcfId for em in ems]

    ms = []


    
    for mcfId in list_of_mcfId:
        statement = db.select(Member).where(Member.mcfId == mcfId)
        m = db.session.scalars(statement).first()
        ms.append(m)

    app.logger.info(ms[0].mcfName)


    statement = db.select(Event).where(Event.id == eventId)
    e = db.session.scalars(statement).first()
    eventName = "_".join(e.tournamentName .split(" "))    
    

    

    for m in ms:
        eventMembers[m.mcfId] = {}
        eventMembers[m.mcfId]["mcfId"] = m.mcfId
        eventMembers[m.mcfId]["mcfName"] = m.mcfName
        eventMembers[m.mcfId]["email"] = m.email
        eventMembers[m.mcfId]["gender"] = m.gender
        eventMembers[m.mcfId]["yearOfBirth"] = m.yearOfBirth
        eventMembers[m.mcfId]["state"] = m.state
        eventMembers[m.mcfId]["nationalRating"] = m.nationalRating
        eventMembers[m.mcfId]["fideId"] = m.fideId
        eventMembers[m.mcfId]["fideName"] = m.fideName
        eventMembers[m.mcfId]["fideRating"] = m.fideRating




    key_1st = next(iter(eventMembers))
    correct_columns = list(eventMembers[key_1st])

    df = pd.DataFrame(eventMembers)

    output = BytesIO()

    # ===== basically reordering internal or 2nd dimension, not the most readable one liner
    df.transpose()[correct_columns].to_csv(output, index=False)


    output.seek(0)
    



    return send_file(output, download_name=
                     "Download_event_members_" +
                     str(datetime.date.today()) +
                     # "_Partial" +
                     # str(downloadOffset) +
                     "_" +
                     eventName +
                     ".csv",
                     as_attachment=True, mimetype="str")



@app.route('/an-evt-ans-download-overwritten')
@admin_required
def an_evt_ans_download_overwritten():


    # query = sa.select(Member).order_by(Member.mcfName)

    whatHappened = ""
    # ===== OrderDict is part of Python already, if you remember what you read in EloquentPython
    # membersAnswers = {}
    membersAnswers = {}

    eventId = request.args['eventId']




    statement = db.select(Event).where(Event.id == eventId)
    e = db.session.scalars(statement).first()
    eventName = "_".join(e.tournamentName .split(" "))    

    

    statement = db.select(FormQuestionAnswersDeleted).where(FormQuestionAnswersDeleted.eventId == eventId)
    fqas = db.session.scalars(statement).all()

    for fqa in fqas:
        unique_key = str(fqa.mcfId) + str(eventId)
        # app.logger.info("$$$$$")
        # app.logger.info(fqa.mcfId)
        # app.logger.info("$$$$$")
        try:
            membersAnswers[unique_key]["mcfId"] = fqa.mcfId
                # "subgroupId": None

            membersAnswers[unique_key][fqa.fieldName] = fqa.answerString
                                                         # "subgroupId": fqa.subgroupId


        except:
            membersAnswers[unique_key] = {}
            membersAnswers[unique_key]["mcfId"] = fqa.mcfId
            membersAnswers[unique_key][fqa.fieldName] = fqa.answerString

    for fqa in fqas:
        unique_key = str(fqa.mcfId) + str(eventId)
        converted_time = fqa.deleted_at.astimezone(pytz.timezone('Asia/Kuala_Lumpur'))
        formatted_time = converted_time.strftime("%d/%m/%Y %H:%M")
        membersAnswers[unique_key]["Deleted on"] = formatted_time


    key_1st = next(iter(membersAnswers))
    correct_columns = list(membersAnswers[key_1st])


    # df = pd.DataFrame()
    # rec = []
    # for m in ms_paginate.items:
    #     rec.append(m.as_dict_for_file("mcf.csv"))
    #     # rec.append(m.as_dict())
        
    # df = df.from_dict(rec)

    # output = BytesIO()
    # df.to_csv(output, index=False)
    # output.seek(0)


    # ===== Example of sample return expected
    # membersAnswers = {
    #     # the key is meaningless and unique, like a primary key in DB, stupid useless to humans but important
    #     "some_mcfIdSome_eventId": {
    #         "mcfId": "1233",
    #         "name": "Ardie",
    #         "gender": "M"
    #     },
    #     "some_mcfIdSome_eventId": {
    #         "mcfId": "1233",
    #         "name": "Hanifa",
    #         "gender": "F"
    #     }
    # }
    
    # df = pd.DataFrame(membersAnswers)
    df = pd.DataFrame(membersAnswers)

    output = BytesIO()

    # ===== basically reordering internal or 2nd dimension, not the most readable one liner
    df.transpose()[correct_columns].to_csv(output, index=False)
    # df = df[correct_columns]x
    output.seek(0)
    

    # return "nothing"
    
    # not sure if mimetype is necessary, can try removing
    # return "nothing burger"
    return send_file(output, download_name=
                     "Download_overwritten_" +
                     str(datetime.date.today()) +
                     # "_Partial" +
                     # str(downloadOffset) +
                     "_" +
                     eventName +
                     ".csv",
                     as_attachment=True, mimetype="str")


@app.route('/get-withdrawal-clause-by-id', methods = ["POS", "GET"])
@login_required
def get_withdrawal_clause_by_id():

    statement = db.select(Event).where(Event.id == request.args.get("eventId"))
    e = db.session.scalars(statement).first()
    return e.withdrawalClause
    
    return "do you agree with a 50% refund?"


if __name__=='__main__': 
    app.run(debug=True)


