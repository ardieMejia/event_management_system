import logging
from flask import Flask, render_template, request, redirect, url_for, send_file
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
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.orm import close_all_sessions
import os
import time
import pandas as pd
from io import StringIO, BytesIO
import datetime

import json




app = Flask(__name__)   # Flask constructor
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login = LoginManager(app)
# app.config['TEMPLATES_AUTO_RELOAD'] = True


from Models.declarative import EventListing # ===== remove this
import sqlalchemy as sa
app.app_context().push()
from model import Event, Member
Session = sessionmaker(bind=db.engine)


from c_templater import C_templater

# ========== CSV
import csv


# ========== CSV




from c_mapper import C_mapper


with app.app_context():
    # db.drop_all()
    close_all_sessions()
    db.engine.dispose()    
    db.drop_all()
    db.create_all()
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



def tryRemoveMcfFile(filename):
    # myfile = "/tmp/foo.txt"
    # If file exists, delete it.
    if os.path.isfile(filename):
        os.remove(filename)
    else:
        pass

def isFileOversized(filename):
    df = pd.read_csv(r'./storage/'+filename)
    if df.size > 500:
        return True
    return False
    
    
@app.route('/single-member/<int:mcfId>', methods = ['GET']) 
def single_member(mcfId):


    query = sa.select(Member).where(Member.mcfId == mcfId)
    m = db.session.scalar(query)
    return render_template("single-member.html", m=m)

@app.route('/single-member-fide/<int:mcfId>', methods = ['GET']) 
def single_member_fide(mcfId):

    
    query = sa.select(Member).where(Member.mcfId == mcfId)
    m = db.session.scalar(query)
    return render_template("single-member-fide.html", m=m)
# return m


@app.route('/update-fide', methods = ['POST']) 
def update_fide():
    mcfId = request.args.get("mcfId")
    # query = sa.select(Member).where(Member.mcfId == mcfId)
    # m = db.session.scalar(query)
    m = db.session(Member).where(Member.mcfId == mcfId )
    m.fideId = request.form['fideId']
    m.fideName = request.form['fideName']
    m.fideRating = request.form['fideRating']
    app.logger.info(m.fideId)
    # TODO: do something about this one
    if m.isDataValid(p_fideId=m.fideId, p_fideRating=m.fideRating):
        errorsList = m.isDataValid(p_fideId=m.fideId, p_fideRating=m.fideRating)
        return C_templater.custom_render_template(errorTopic="Invalid Input Error", errorsList=errorsList, isTemplate=True)
    

    db.session.add(m)
    try:
        db.session.commit()
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        return C_templater.custom_render_template(errorTopic="DB-API IntegrityError", errorsList=[i._message], isTemplate=True)
    except DataError as d:
        db.session.rollback()
        return C_templater.custom_render_template(errorTopic="DB API DataError", errorsList=[d._message], isTemplate=True)


    
    # return "new FIDE saved"
    return render_template("single-member.html", m=m, whatHappened="new FIDE saved")

@app.route('/event-create')
def event_create():
    app.logger.info('========== event ==========')
    app.logger.info('========== event ==========')
    
    return render_template("event-create.html", el=Event.disciplinesList)

# @app.route('/member-create')
# def member_create():
#     app.logger.info('========== member ==========')
#     app.logger.info('========== member ==========')
    
#     return render_template("member-create.html")




@app.route('/test2') 
def test2():
    query = db.select(Member).where(Member.fideId != None)
    # ms_paginate=db.paginate(query, page=page, per_page=20, error_out=False)
    ms = db.session.execute(query).all()

    app.logger.info(ms)

    return "something"


@app.route('/member-update-page/<int:mcfId>')
def member_update_page(mcfId):

    query = sa.select(Member).where(Member.mcfId == mcfId)
    m = db.session.scalar(query)

    query = sa.select(Event)
    es = db.session.scalars(query).all()

    
    return render_template("member-update-page.html", m=m, es=es)






@app.route('/update-member', methods = ['POST']) 
def update_member():                

    # app.logger.info('========== event ==========')
    # app.logger.info(request.form.keys())
    # app.logger.info('========== event ==========')
    # return "what"

    app.logger.info("==========")
    app.logger.info(request.form.get("mcfId"))
    app.logger.info(request.form)
    app.logger.info(request.form.get("button"))
    app.logger.info("==========")
    m = db.session.query(Member).get(request.form['mcfId'])
    # e = db.session.query(Event).get(request.form['events'])

    m_events = m.getEvents().split(",")
    if request.form.get("button") == "save":
        # overwrite only if event non existing in m.events
        if request.form['mcfId'] not in m_events:        
            m.events = m.getEvents() + "," + request.form.get("discipline") # WARNING: this is slightly unreadable            
    elif request.form.get("button") == "delete":
        try: m_events.remove(request.form.get("discipline"))
        except: pass # becoz .remove can produce errors
        m.events = ",".join(m_events)

        
    
    # m.events.append(e)
    # e.members.append(m)

    # if re                       # 
        
        

    # if 1 == 0:
    try:
        db.session.commit()
    except IntegrityError as i:
        db.session.rollback()
        return C_templater.custom_render_template(errorTopic="DB-API IntegrityError", errorsList=[i._message], isTemplate=True)
    
    # app.logger.info('========== event ==========')
    # app.logger.info('========== event ==========')

    return "update successfully"



@app.route('/create-event', methods = ['POST']) 
def create_event():
    
    with session_scope() as session:
        e = Event(tournamentName=request.form['tournamentName'], startDate=request.form['startDate'], endDate=request.form['endDate'], discipline=request.form['discipline'])

    
        if e.isDataInvalid(p_tournameName=e.tournamentName, p_startDate=e.startDate, p_endDate=e.endDate, p_discipline=e.discipline):
            errorsList = e.isDataInvalid(p_tournameName=e.tournamentName, p_startDate=e.startDate, p_endDate=e.endDate, p_discipline=e.discipline)
            return C_templater.custom_render_template(errorTopic="Invalid Input Error", errorsList=errorsList, isTemplate=True)


        e.id = e.set_id()
        db.session.add(e)
        db.session.commit()

    
    
        # try:
        #     db.session.commit()
        # except IntegrityError as i:
        #     db.session.rollback()
        # return C_templater.custom_render_template(errorTopic="DB-API IntegrityError", errorsList=[i._message], isTemplate=True)
        # this ones good ===== return c_templater("Data entry error", "tournament name duplicate", "error.html")
        


        return render_template("confirmed-event-created.html", e=e)


@app.route('/create-member', methods = ['POST'])
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
        return C_templater.custom_render_template(errorTopic="DB-API IntegrityError", errorsList=[i._message], isTemplate=True)
    # example of final form ===== return c_templater("Data entry error", "tournament name duplicate", "error.html")
        
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))
    app.logger.info(m)
    app.logger.info('========== event ==========')


    # return C_templater.custom_render_template("Successfully saved", i._message())
    return redirect('/members', whatHappened="New member successfully saved")




@app.route('/kill-event/<int:id>') 
def kill_event(id):
    
    
    stmt = sa.delete(Event).where(Event.id == id)
    db.session.execute(stmt)
    db.session.commit()
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))
    app.logger.info(id)
    app.logger.info('========== event ==========')

    query = sa.select(Event)
    es = db.session.scalars(query).all()

    # return "event successfully removed"
    return render_template("events.html", es=es, whatHappened="Event successfully killed")


@app.route('/kill-events') 
def kill_events():
    
    
    stmt = sa.delete(Event)
    db.session.execute(stmt)
    db.session.commit()


    query = sa.select(Event)
    es = db.session.scalars(query).all()

    # return "member successfully removed"
    return render_template("events.html", es=es, whatHappened="All killed")


@app.route('/kill-member/<int:mcfId>') 
def kill_member(mcfId):
    
    
    stmt = sa.delete(Member).where(Member.mcfId == mcfId)
    db.session.execute(stmt)
    db.session.commit()
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))
    app.logger.info(mcfId)
    app.logger.info('========== event ==========')

    query = sa.select(Member)
    ms = db.session.scalars(query).all()

    # return "member successfully removed"
    return render_template("members.html", ms=ms, whatHappened="Member successfully killed")

@app.route('/kill-members') 
def kill_members():
    
    
    stmt = sa.delete(Member)
    db.session.execute(stmt)
    db.session.commit()


    query = sa.select(Member)
    ms = db.session.scalars(query).all()

    # return "member successfully removed"
    return render_template("members.html", ms=ms, whatHappened="All killed")



@app.route('/events') 
def find_events():
    
    # e = Event(tournamentName=request.form['tournamentName'], startDate=request.form['startDate'], endDate=request.form['endDate'], discipline=request.form['discipline'])
    # db.session.add(e)
    # db.session.commit()

            

    es = None
    # with session_scope() as session:
    #     try:
    #         es = session.query(Event).all()
    #         # m = sa.select(Event)
    #         # es = db.session.scalars(query).all()
    #     except Exception as e:
    #         session.rollback()
    #         return f"An error occurred: {str(e)}", 500
        

    try:
        es = db.session.query(Event).all()
        # m = sa.select(Event)
        # es = db.session.scalars(query).all()
    except Exception as e:
        session.rollback()
        return f"An error occurred: {str(e)}", 500    

    # if not es:
    #     return render_template("events.html")
        
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))
    app.logger.info('========== event ==========')
    
    db.session.close()

    return render_template("events.html", es=es)


@app.route('/members') 
def find_members():

    page = request.args.get("page", 1, type=int)
    
    query = sa.select(Member).order_by(Member.mcfName)
    ms_paginate=db.paginate(query, page=page, per_page=20, error_out=False)
    # ms = db.session.scalars(query).all()

    # prev_url = "a_page/page=23"
    prev_url = url_for("find_members", page=ms_paginate.prev_num)
    next_url = url_for("find_members", page=ms_paginate.next_num)


    # https://stackoverflow.com/questions/14754994/why-is-sqlalchemy-count-much-slower-than-the-raw-query
    statement = db.session.query(db.func.count(Member.mcfId))
    count = db.session.scalars(statement).first() # coz I dont know a better/faster way to count records

    app.logger.info('========== event ==========')
    app.logger.info(ms_paginate)
    app.logger.info('========== event ==========')
    db.session.close()
    
    # return "wait"
    # ms_dict = [m.__dict__ for m in ms]
    return render_template("members.html", ms=ms_paginate.items, prev_url=prev_url, next_url=next_url, page=page, totalPages=ms_paginate.pages, totalCount=count)

                    






                    



@app.route('/') 
def main_page():
    return render_template("main-page.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if current_user.is_authenticated:
            return redirect(url_for('main_page'))

        mcfId = request.form['mcfId']
        password = request.form['password']

        # app.logger.info('========== ---------- ++++++++++')
        # app.logger.info('Received data:', mcfId , password)
        # app.logger.info('========== ---------- ++++++++++')


        m = Member.query.filter_by(mcfId=mcfId).first()
        if m is None:
            # return "member ID does NOT exist"
            return C_templater.custom_render_template("Login Problem", ["Member does not exist"], True)        
        # isPasswordVerified = bcrypt.check_password_hash(bcrypt.generate_password_hash(password).decode('utf-8'), m.password)
        
        if not m.check_password(password):    
            return C_templater.custom_render_template("Login Problem", ["Wrong password"], True)
        else:
            es = []
            login_user(m)
            query = sa.select(Event)
            es = db.session.scalars(query).all()
            tr = []
            if m.getEvents():
                for e in m.getEvents().split(","):            
                    statement = db.select(Event).where(Event.id == e)
                    e = db.session.scalars(statement).first()
                    tr.append(e.tournamentName)
                        
            return render_template("member-front.html", m=m, tournamentRegistered=tr, tournamentOptions=es)

    else:
        return render_template("login.html")



    
    
@app.route('/member-front')
def member_front():

    if current_user.is_authenticated:
        m = Member.query.filter_by(mcfId=current_user.mcfId).first()
        query = sa.select(Event)
        es = db.session.scalars(query).all()


        tr = []
        for e in m.getEvents().split(","):
            if e:
                # app.logger.info(e)
                statement = db.select(Event).where(Event.id == e)
                e = db.session.scalars(statement).first()
                tr.append(e.tournamentName)
            
        app.logger.info("+++++")
        app.logger.info(tr)
        app.logger.info("+++++")



        return render_template("member-front.html", m=m, tournamentRegistered=tr, tournamentOptions=es)
    else:
        return render_template("login.html")




    


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main_page'))


@app.route('/bulk-upload-events-csv')
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
                app.logger.info(i._message())
                return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)        


    # return C_templater.custom_render_template("Successfull bulk upload", "event data", False)
# return redirect('/events')
    return render_template("main-page.html", whatHappened="Upload successfull and no duplicate or other issues")





@app.route('/bulk_upload_members_csv')
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
            app.logger.info(i._message())
                # return C_templater.custom_render_template("Data entry error", i._message(), False)
            return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)
        

        if not duplicatesList:            
            whatHappened = "Upload successful with no duplicates"
        else:
            whatHappened = "Upload successful with some duplicates"




        

    return render_template("main-page.html", whatHappened=whatHappened, whyHappened=duplicatesList)



@app.route('/bulk_upload_fide_csv')
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
            return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)        
        
            # query = sa.select(Member).where(Member.mcfId == row[''])
            # f = db.session.scalar(query)
            # m.fide = f                           


        try:
            db.session.commit()
        except IntegrityError as i:
            db.session.rollback()
            app.logger.info(i._message())
                # return C_templater.custom_render_template("Data entry error", i._message(), False)
            return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)        

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
    df = pd.read_csv(r'./storage/'+filename, usecols=wanted_columns, chunksize=chunksize, dtype=str)


    skippedList = []
    newList = []
    for chunk in df:
        app.logger.info("==========")
        # app.logger.info(type(chunk))
        # app.logger.info(chunk)
        app.logger.info("==========")
        values=[]
        
        for index, row in chunk.iterrows():

            if Member.doesUserExist(row[mapFrom['mcfId']]):
                skippedList.append({"mcfId": row[mapFrom['mcfId']]})
                continue

            values.append(
                {
                    "mcfId": row[mapFrom['mcfId']],
                    "mcfName": row[mapFrom['mcfName']],
                    "gender": row[mapFrom['gender']],
                    "yearOfBirth": row[mapFrom['yearOfBirth']],
                    "state": row[mapFrom['state']],
                    "nationalRating": row[mapFrom['nationalRating']],
                    "events": "",
                    "fideId": Member.empty_string_to_zero(num = str(row[mapFrom['fideId']])),
                    "password": bcrypt.generate_password_hash(row[mapFrom['mcfId']].strip() \
                                                              + row[mapFrom['yearOfBirth']].strip() \
                                                              ).decode('utf-8')
                }
            )
            newList.append({"mcfId": row[mapFrom['mcfId']]})

            app.logger.info("==========")
            app.logger.info(values)
            app.logger.info("==========")
            
    
        try:
            statement = db.insert(Member)
            db.session.execute(statement, values)
            db.session.commit()

        except IntegrityError as i:
            db.session.rollback()
            app.logger.info(i._message())
            # return C_templater.custom_render_template("Data entry error", i._message(), False)
            return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)


    if not skippedList:            
        whatHappened = "No records skipped"
    else:
        whatHappened = "Some skipped records"


    return whatHappened, skippedList, newList



   

def processFideList():
    filename = "frl.csv"
    whyHappened = []

    mapFrom = C_mapper.excelToDatabase[filename]
    with open(r'./storage/'+filename, newline='') as csvfile:
        dictreader = csv.DictReader(csvfile, delimiter=',')
        for row in dictreader:


            statement = db.select(Member).where(Member.fideId == row[mapFrom['fideId']])
            m = db.session.scalars(statement).first()
            if m:                          
                m.fideId=row[mapFrom['fideId']]
                m.fideName=row[mapFrom['fideName']]                       
                m.fideRating=row[mapFrom['fideRating']]                           
            else:
                whyHappened.append({
                    "fideId": row[mapFrom['fideId']],
                    "fideName": row[mapFrom['fideName']],
                    "fideRating": row[mapFrom['fideRating']]
                                    })

        # ===== try uploading bulk    
    try:
        db.session.commit()

    except IntegrityError as i:
        db.session.rollback()
        app.logger.info(i._message())
        # return C_templater.custom_render_template("Data entry error", i._message(), False)
        return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)

    if not whyHappened:            
        whatHappened = "Upload successful with no inconsistencies"
    else:
        whatHappened = "Upload successful BUT with the FIDE ID listed with no matching MCF ID"

        

    app.logger.info(whyHappened)


    return whatHappened, whyHappened




def updateMcfList():
    filename="mcf.csv"


    mapFrom = C_mapper.excelToDatabase[filename]
    
    wanted_columns = [mapFrom['mcfId'], mapFrom['mcfName'], mapFrom['gender'], mapFrom['yearOfBirth'], mapFrom['state'], mapFrom['nationalRating'], mapFrom['fideId']]


    df = pd.read_csv(r'./storage/'+filename, usecols=wanted_columns, dtype=str)





    
    updatesList = []
    failedUpdatesList = []
    skippedList = []
    for index,row in df.iterrows():
        app.logger.info("==========")
        # app.logger.info(type(chunk))
        # app.logger.info(chunk)
        app.logger.info("==========")
        values=[]
        

        m = Member.query.filter_by(mcfId=row[mapFrom['mcfId']]).first()


        if m:
            m.mcfName = row[mapFrom['mcfName']]
            m.gender = row[mapFrom['gender']]
            m.yearOfBirth = row[mapFrom['yearOfBirth']]
            m.state = row[mapFrom['state']]
            m.nationalRating = row[mapFrom['nationalRating']]
            m.fideId = row[mapFrom['fideId']]
            m.password = bcrypt.generate_password_hash(row[mapFrom['mcfId']].strip() \
                                                       + row[mapFrom['yearOfBirth']].strip() \
                                                       ).decode('utf-8')
            updatesList.append({"mcfId": row[mapFrom['mcfId']]})
        else:
            skippedList.append({"mcfId": row[mapFrom['mcfId']]})

            
        


                
        try:
            db.session.commit()
        except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
            # whatHappened = "DB-API IntegrityError"
            failedUpdatesList.append("DB-API IntegrityError")
            db.session.rollback()
            # return C_templater.custom_render_template(errorTopic="DB-API IntegrityError", errorsList=[i._message], isTemplate=True)
        except DataError as d:
            failedUpdatesList.append("DB API DataError")
            db.session.rollback()
            # return C_templater.custom_render_template(errorTopic="DB API DataError", errorsList=[d._message], isTemplate=True)


    if not updatesList and not failedUpdatesList:            
        whatHappened = "No updated records"
    if not updatesList and failedUpdatesList:            
        whatHappened = "No updated records with failed update details below"
    else:
        whatHappened = "Updated record details below"


    tryRemoveMcfFile("./storage/mcf.csv")                
                


    return whatHappened, updatesList, failedUpdatesList, skippedList



def updateFrlList():
    return "mpthing", "nptin"



@app.route('/bulk-process-all-mcf')
def bulk_process_all_mcf():

    fileOversized = isFileOversized("mcf.csv")
    if fileOversized:
        whatHappened, skippedList, newList= "File is too large (> 500)", [], []
    else:
        whatHappened, skippedList, newList = processMcfList()

    return render_template("main-page.html", whatHappened=whatHappened, skippedList=skippedList, newList=newList)


@app.route('/bulk-process-all-frl')
def bulk_process_all_frl():
    whatHappened, whyHappened = processFideList()

    return render_template("main-page.html", whatHappened=whatHappened, whyHappened=whyHappened)


@app.route('/bulk-update-all-mcf')
def bulk_update_all_mcf():
    # if not os.path.isfile("./storage/mcf.csv"):
    #     return C_templater.custom_render_template(errorTopic="Invalid Upload Name", errorsList=["files must be a csv and contain \"mcf\" in its filename"], isTemplate=True)
    # ===== failedUpdatesList: for now only the length of the list is used in the template
    fileOversized = isFileOversized("mcf.csv")
    if fileOversized:
        whatHappened, updatesList, failedUpdatesList, skippedList = "File is too large (> 500)", [], [], []
    else:        
        whatHappened, updatesList, failedUpdatesList, skippedList = updateMcfList()

    return render_template("main-page.html", whatHappened=whatHappened, updatesList=updatesList, failedUpdatesList=failedUpdatesList, skippedList=skippedList)







def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def allowed_bulk_upload(filename):
    # return True
    return "mcf" in filename.lower() or "frl" in filename.lower()
    # return '.' in filename and \
    #        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/bulk-upload-all-files_1', methods=['POST'])
def bulk_upload_all_files_1():

    
    # app.logger.info("==========")
    # app.logger.info(request.files)
    
    # if 'file' not in request.files:
        # return redirect(request.url)
        
    file1 = request.files['file1']


    if file1.filename == '':
        return render_template("main-page.html", whatHappened="File must be named mcf.csv", whyHappened=[])


    app.logger.info("==========")
    app.logger.info(allowed_bulk_upload(file1.filename))
    if file1 \
       and allowed_bulk_upload(file1.filename):
        filename1 = secure_filename(file1.filename)
        file1.save(os.path.join('./storage/mcf.csv'))
        # filename2 = secure_filename(file2.filename)
        # file2.save(os.path.join('./storage/', filename2.lower()))
        # return 'File successfully uploaded'
        return render_template("main-page.html", whatHappened="MCF file successfully uploaded")
    else:
        return C_templater.custom_render_template("Invalid Upload Name", [format(app.config['ALLOWED_EXTENSIONS']), "files must be named either mcf.csv"], True)
        # return 'Invalid file type'
    # return "wait"


    
@app.route('/bulk-upload-all-files_2', methods=['POST'])
def bulk_upload_all_files_2():

    
    # app.logger.info("==========")
    # app.logger.info(request.files)
    
    # if 'file' not in request.files:
        # return redirect(request.url)
        
    file2 = request.files['file2']

    if file2.filename == '':
        return render_template("main-page.html", whatHappened="File must be named frl.csv", whyHappened=[])


    app.logger.info("==========")
    app.logger.info(allowed_bulk_upload(file2.filename))
    if file2 \
       and allowed_bulk_upload(file2.filename):
        filename2 = secure_filename(file2.filename)
        file2.save(os.path.join('./storage/frl.csv'))
        # return 'File successfully uploaded'
        return render_template("main-page.html", whatHappened="Both files successfully uploaded")
    else:
        return C_templater.custom_render_template("Invalid Upload Name", [format(app.config['ALLOWED_EXTENSIONS']), "files must be named either frl.csv"], True)
        # return 'Invalid file type'
    # return "wait"

    

@app.route('/test_bulk_download') 
def test_bulk_download():
    """Dont Delete This Function. this is to self-document

    This function shows difference of converting SQLAlchemy results
    to dicts"""

    range = 100

    query = sa.select(Member).order_by(Member.mcfName)
    some_object = db.session.query(Member).order_by(Member.mcfName).offset(100).limit(100)

    ms_paginate=db.paginate(query, page=1, per_page=100, error_out=False)
    # ms_paginate2=db.paginate(query, page=1, per_page=100, error_out=False)
    # results = session.query(Member).all()

    df = pd.DataFrame()

    rec = []
    for m in ms_paginate.items:
        rec.append(m.as_dict_for_file("mcf.csv"))
        
    df = df.from_dict(rec)

    # df = pd.DataFrame(
    #     {
    #         "Name": ["Tesla", "Tesla", "Toyota", "Ford", "Ford", "Ford"],
    #         "Type": ["Model X", "Model Y", "Corolla", "Bronco", "Fiesta", "Mustang"],
    #     }
    # )


    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)

    # return render_template("members.html", ms=ms_paginate.items, prev_url=prev_url, next_url=next_url, page=page, totalPages=ms_paginate.pages)
    
    return send_file(output, download_name="haha.csv", as_attachment=True, mimetype="str") # not sure if mimetype is necessary, can try removing when free

@app.route('/partial-download') 
def partial_download():


    
    downloadOffset = request.args.get("downloadOffset", type=int)

    query = sa.select(Member).order_by(Member.mcfName)
    ms_paginate=db.paginate(query, page=downloadOffset, per_page=500, error_out=False)


    var1 = ms_paginate.items[0]
    app.logger.info(var1.events)
    
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

    # return "nothing burger"
     


if __name__=='__main__': 
    app.run(debug=True)


