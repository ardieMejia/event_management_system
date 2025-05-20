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
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.orm import close_all_sessions
import os
import time
import pandas as pd
from io import StringIO, BytesIO
import datetime
# from c_validation_funcs import convert_nan_to_string
from c_validation_funcs import validate_before_saving

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
from model import Event, Member, File, FormQuestion, EventMember, FormQuestionAnswers
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
    if os.path.isfile(r'./storage/'+filename):
        return True
    return False


def isFileOversized(filename):

    df = pd.read_csv(r'./storage/'+filename)

    if len(df) > 502:
        return True
    return False
    
    
@app.route('/single-member/<int:mcfId>', methods = ['GET']) 
def single_member(mcfId):


    query = sa.select(Member).where(Member.mcfId == mcfId)
    m = db.session.scalar(query)
    return render_template("single-member.html", m=m)

@app.route('/single-member-fide/<int:mcfId>', methods = ['GET']) 
def single_member_fide(mcfId):

    whatHappened = request.args.get("whatHappened")
    if not whatHappened:
        whatHappened=""
    query = sa.select(Member).where(Member.mcfId == mcfId)
    m = db.session.scalar(query)
    return render_template("single-member-fide.html", m=m, whatHappened=whatHappened)
# return m


@app.route('/update-fide', methods = ['POST']) 
def update_fide():
    mcfId = request.args.get("mcfId")
    # query = sa.select(Member).where(Member.mcfId == mcfId)
    # m = db.session.scalar(query)
    # m = db.session(Member).where(Member.mcfId == mcfId )


    statement = db.select(Member).where(Member.mcfId == mcfId)
    m = db.session.scalars(statement).first()
    m.fideId = request.form['fideId']
    m.fideName = request.form['fideName']
    m.fideRating = request.form['fideRating']
    app.logger.info(m.fideId)
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
        whatHappened = "something went wrong"
        
    except DataError as d:
        db.session.rollback()
        # return C_templater.custom_render_template(errorTopic="DB API DataError", errorsList=[d._message], isTemplate=True)
        whatHappened = "something went wrong"


    # db.session.close() # we are eager to close session after last times error in production
    

    return redirect(url_for('member_front', whatHappened=whatHappened))
    # return render_template("member-front.html", m=m, tournamentRegistered=tr, tournamentOptions=es, whatHappened=whatHappened)



@app.route('/event-create')
def event_create():

    
    return render_template("event-create.html", dl=Event.disciplinesList, tl=Event.typeList, el=Event.eligibilityList, ll=Event.limitationList, rl=Event.roundsList, tcl=Event.timeControlList)

# @app.route('/member-create')
# def member_create():
#     app.logger.info('========== member ==========')
#     app.logger.info('========== member ==========')
    
#     return render_template("member-create.html")




@app.route('/test2') 
def test2():
    # query = db.select(Member).where(Member.fideId != None)
    # ms_paginate=db.paginate(query, page=page, per_page=20, error_out=False)
    # ms = db.session.execute(query).all()

    # app.logger.info(ms)

    # 1746603668



    return "wait"


@app.route('/member-update-page/<int:mcfId>')
def member_update_page(mcfId):

    query = sa.select(Member).where(Member.mcfId == mcfId)
    m = db.session.scalar(query)

    query = sa.select(Event)
    es = db.session.scalars(query).all()

    
    return render_template("member-update-page.html", m=m, es=es)










@app.route('/create-event', methods = ['POST']) 
def create_event():
    
    with session_scope() as session:
        e = Event(tournamentName=request.form['tournamentName'], startDate=request.form['startDate'], endDate=request.form['endDate'], discipline=request.form['discipline'], type=request.form['type'], eligibility=request.form['eligibility'], limitation=request.form['limitation'], rounds=request.form['rounds'], timeControl=request.form['timeControl'])

    
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
        

        return redirect(url_for('find_events'))

        # return render_template("confirmed-event-created.html", e=e)


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
        
    # app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))
    # app.logger.info(m)
    # app.logger.info('========== event ==========')


    # return C_templater.custom_render_template("Successfully saved", i._message())
    return redirect('/members', whatHappened="New member successfully saved")




@app.route('/kill-event/<int:id>') 
def kill_event(id):
    
    
    stmt = sa.delete(Event).where(Event.id == id)
    db.session.execute(stmt)
    db.session.commit()
    
    try:
        db.session.commit()
        whatHappened = "events deleted across all members"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened = "something went wrong"
    db.session.close()




    stmt = sa.delete(EventMember).where(EventMember.eventId == id)
    db.session.execute(stmt)
    db.session.commit()

    try:
        db.session.commit()
        whatHappened = "events deleted across all members"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened = "something went wrong"
    db.session.close()

    
    query = sa.select(Event)
    es = db.session.scalars(query).all()
    db.session.close()
    
    return render_template("events.html", es=es, whatHappened="Event successfully killed")


@app.route('/kill-events') 
def kill_events():

    whatHappened = ""    

    stmt = sa.delete(Event)
    db.session.execute(stmt)

    
    try:
        db.session.commit()
        whatHappened = "all events deleted, "
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened = "something went wrong, contact the web app dev"

        
    stmt = sa.delete(EventMember)
    db.session.execute(stmt)

    try:
        db.session.commit()
        whatHappened = "all member-events relations deleted"
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        whatHappened = "something went wrong, contact the web app dev"

    
    query = sa.select(Event)
    es = db.session.scalars(query).all()

    db.session.close()


    return render_template("events.html", es=es, whatHappened=whatHappened)


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
        db.session.rollback()
        return f"An error occurred: {str(e)}", 500    

    # if not es:
    #     return render_template("events.html")
        
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))
    app.logger.info('========== event ==========')
    
    db.session.close()



    whatHappened = request.args.get("whatHappened")
    if not whatHappened:
        whatHappened = ""

    return render_template("events.html", es=es, whatHappened=whatHappened)



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
    whatHappened = request.args.get('whatHappened')
    if not whatHappened:
        whatHappened = ""
    return render_template("main-page.html", whatHappened=whatHappened)


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
            return render_template("login.html", whatHappened = "Member does not exist")

        
        if not m.check_password(password):    
            # return C_templater.custom_render_template("Login Problem", ["Wrong password"], True)
            return render_template("login.html", whatHappened = "Ooops, wrong password")
        else:
            login_user(m)
            query = sa.select(Event)
            es = []
            es = db.session.scalars(query).all()

            
            
            tr = []

            statement = db.select(EventMember).where(EventMember.mcfId == current_user.mcfId)
            ems = db.session.execute(statement).all()

            tr = []

            # if m.getEvents() != "":
            #     for e in m.getEvents():            
            #         statement = db.select(Event).where(Event.id == e)
            #         e = db.session.scalars(statement).first()
            #         tr.append(e.tournamentName)
                        
            return render_template("member-front.html", m=m, tournamentRegistered=tr, tournamentOptions=es)
            

    else:
        return render_template("login.html")





@app.route('/form-submission', methods = ['POST'])
def form_submission():
    if current_user.is_authenticated:
        whatHappened = ""
        # app.logger.info("==========")    
        # app.logger.info(dir(request.args) )    
        app.logger.info(request.form.keys() )
        app.logger.info(request.form.get("fullname") )
        app.logger.info(request.form.listvalues())

        eventId = request.form['eventId']


        answers = []
        for fieldname,answer in request.form.items():
            if fieldname == "eventId":
                continue
            app.logger.info("********")
            app.logger.info(answer)
            fqa = FormQuestionAnswers(
                mcfId=current_user.mcfId,
                fieldName=fieldname,
                eventId=eventId,
                answerString=answer
            )
            answers.append(fqa)
            
        db.session.add_all(answers)
    
        try:
            db.session.commit()
            whatHappened = "answers successfully recorded"
        except IntegrityError as i:
            db.session.rollback()
            whatHappened = "something went wrong, answers failed to save, please re-fill form"
            # endforloopanswers

        return redirect(url_for('member_front', whatHappened=whatHappened))
        # return "nothing here"

        
        


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
    
    return render_template('form-question-answers.html', membersAnswers=membersAnswers, whatHappened=whatHappened)



@app.route('/event-answers-page', methods = ['POST'])
def event_answers_page():
    whatHappened = ""

    eventId = request.form.get('eventId')

    statement = db.select(FormQuestionAnswers).where(FormQuestionAnswers.eventId == eventId)
    fqas = db.session.scalars(statement).all()


    app.logger.info(eventId)
    app.logger.info(eventId)
    app.logger.info(eventId)


    app.logger.info(fqas)
    app.logger.info(eventId)
    membersAnswers = {}

    for fqa in fqas:
        unique_key = str(fqa.mcfId) + str(eventId)
        try:
            membersAnswers[unique_key]["mcfId"] = fqa.mcfId
            membersAnswers[unique_key][fqa.fieldName] = fqa.answerString
        except:
            membersAnswers[unique_key] = {}
            membersAnswers[unique_key]["mcfId"] = fqa.mcfId
            membersAnswers[unique_key][fqa.fieldName] = fqa.answerString

    app.logger.info(
        
    membersAnswers
    )
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
    
    return render_template('event-answers-page.html', membersAnswers=membersAnswers, whatHappened=whatHappened)


        
@app.route('/form-template', methods = ['GET'])
def form_template():


    eventId = request.args.get("eventId")

    

    statement = db.select(FormQuestion).where(FormQuestion.eventId == eventId)
    frs = db.session.scalars(statement).all()
    if not frs:
        return redirect(url_for("member_front", whatHappened="No form for this event yet"))


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
    # - so it becomes eg: nametext, genderdropdown, agetext
    a_dict = {}
    for fr_dict in frs_list:
        fieldtype_key = fr_dict["fieldName"]+fr_dict["type"]
        
        if fr_dict["type"] == "dropdown" or fr_dict["type"] == "checkbox":
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
            # endtext


    elements = list(a_dict.values())

        
    # ===== Example of return data expected, unique ID is useless in template, only serves as organization
    # elements = {
    #     "genderdropdown" : {
    #         "value": ["M", "F", "Open"], "field": "gender", "type" : "text"
    #     },
    #     "fullicnametext" : {
    #         "value": "", "field": "fullname", "type" : "dropdown"
    #     }
    # }
    
    return render_template("form-template.html", elements=elements, eventId=eventId)






@app.route('/event-form-creator', methods = ['POST', 'GET'])
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
            return redirect(url_for('event_form_creator', whatHappened="Lets get creating1", eventId=eventId))
        if request.form.get("button") == "add":
            if request.form.get("type") == "dropdown" or request.form.get("type") == "checkbox":
                values = request.form.get("value").split("::")
                app.logger.info(request.form.get("_______"))
                app.logger.info(request.form.get("questionstring"))
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
                    except IntegrityError as i:
                        app.logger.info("enderror")
                        db.session.rollback()
                        return redirect(url_for('event_form_creator', whatHappened="something went wrong when committing dropdowns", eventId=eventId))
                #enddropdownorcheckbox
                return redirect(url_for('event_form_creator', whatHappened="dropdown created", eventId=eventId))
            else: 
                fr = FormQuestion(eventId=eventId,
                                   fieldName=request.form.get("field"),
                                   value="",
                                   questionstring=request.form.get("questionstring"),
                                   type=request.form.get("type")
                                   )
                try:
                    db.session.add(fr)
                    db.session.commit()
                except IntegrityError as i:
                    app.logger.info("enderror")
                    app.logger.info(fr)
                    db.session.rollback()
                    #endnotdropdown
                    return redirect(url_for('event_form_creator', whatHappened="something went wrong", eventId=eventId))
                #endadd
                return render_template("event-form-creator.html", whatHappened="text field created", eventId=eventId)
        else:
            # form_elements = [
            #     {
            #         "dropdown" : ["M", "F", "Open"]
            #     }
            # ]
            form_vars = ""
            app.logger.info("endNotDropdown")
            # enddone
            return redirect(url_for("main_page",whatHappened="form creation loop finished"))
        # endpost

        
def kill_form_descendents_by_id(eventId):

    whatHappened = ""
    statement = sa.select(Event).where(Event.id == eventId)
    e = db.session.scalars(statement).first()
    tournamentName = e.tournamentName

    statement = sa.delete(FormQuestion).where(FormQuestion.eventId == eventId)
    db.session.execute(statement)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return None, "something went wrong"

    statement = sa.delete(FormQuestionAnswers).where(FormQuestionAnswers.eventId == eventId)
    db.session.execute(statement)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return None, "something went wrong"


    return tournamentName, whatHappened

    
@app.route('/kill-form-descendents', methods = ["POST"])
def kill_form_descendents():
    
    whatHappened = ""
    eventId = request.form.get('eventId')
    if not eventId:
        eventId = request.args.get('eventId')


    tournamentName, whatHappened = kill_form_descendents_by_id(eventId)
    if tournamentName:
        whatHappened="All derived form data of " + tournamentName + " killed"

    return redirect(url_for('main_page', whatHappened=whatHappened))

    
    
    

    
    
@app.route('/member-front', methods=['GET', 'POST'])
def member_front():
    if current_user.is_authenticated:
        if request.method == 'GET':
            trnames = []
            paymentProofs = []
            m = Member.query.filter_by(mcfId=current_user.mcfId).first()
            query = sa.select(Event)
            es = db.session.scalars(query).all()

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
                    trnames.append(e.tournamentName)
            

                    # trnames.append(e.tournamentName)
            app.logger.info("%%%%%%%")
            app.logger.info(trnames)

                
            if not whatHappened:
                whatHappened = ""

            app.logger.info("********")
            app.logger.info(whatHappened)

            # endget
            return render_template("member-front.html", m=m, tournamentRegistered=trnames, tournamentOptions=es, whatHappened=whatHappened, paymentProofs=paymentProofs)
        else:
            paymentProofs = []
            # app.logger.info("==========")
            # app.logger.info(request.form.get("mcfId"))
            # app.logger.info(request.form)
            # app.logger.info(request.form.get("button"))
            # app.logger.info("==========")

            
            whatHappened=""
            if request.form.get("button") == "save":
                # overwrite only if event non existing in m.events

                statement = db.select(EventMember).where(EventMember.mcfId == current_user.mcfId, EventMember.eventId == request.form["tournament_name"])
                res = db.session.execute(statement).first()
                # app.logger.info("eeeeeeee")
                # app.logger.info(request.form["tournament_name"])
                if not res:
                    em = EventMember(mcfId=current_user.mcfId, eventId=request.form["tournament_name"])
                    db.session.add(em)
                try:
                    db.session.commit()
                    whatHappened="Saved: "
                except IntegrityError as i: 
                    db.session.rollback()
                    whatHappened = "something went wrong, contact your web dev"                

                    
                    # endsavebutton
            elif request.form.get("button") == "delete":


                em = EventMember(mcfId=current_user.mcfId, eventId=request.form["tournament_name"])
                statement = sa.delete(EventMember).where(EventMember.mcfId == current_user.mcfId, EventMember.eventId == request.form["tournament_name"])
                db.session.execute(statement)

                try:
                    db.session.commit()
                except IntegrityError as i:
                    db.session.rollback()
                    whatHappened = "something went wrong"

                
                # enddeletebutton
            elif request.form.get("button") == "fillForm":
                eventId = request.form["tournament_name"]


                
                # endfillformsample
                return redirect(url_for('form_template', eventId=eventId))


                



    


            db.session.close()

            # endpost
            return redirect(url_for('member_front', whatHappened=whatHappened, updatedTournamentId=request.form.get("tournament_name"), paymentProofs=paymentProofs))

    else:
        # endnotauthenticated
        return render_template("login.html")
        



@app.route('/upload-payment-proof', methods = ['GET', 'POST'])
def upload_payment_proof():
    if current_user.is_authenticated:
        paymentProofs = []
        paymentFile = request.files['paymentFile']
        if paymentFile.filename == '':
            # endemptycheck
            return redirect(url_for('member_front', whatHappened="Error: There is no file uploaded", updatedTournamentId="", paymentProofs=paymentProofs))


        if paymentFile and allowed_payment_file(paymentFile.filename):
            filename = secure_filename(paymentFile.filename)
            fname, ext = os.path.splitext(paymentFile.filename)
            # disk_path = ""  # Path to the persistent disk
            # folder_name = "my_folder"
            # folder_path = os.path.join(disk_path, folder_name)
            folder_path = os.path.join(f"storage", str(datetime.date.today()))
        
            try:
                os.makedirs(folder_path, exist_ok=True)
                # print(f"Folder '{folder_name}' created successfully at '{folder_path}'.")
            except Exception as e:            
                return redirect(url_for('member_front', whatHappened="Error: Something went wrong. Please contact web admin", paymentProofs=paymentProofs))

                
                
            # ===== use os.path.join with care, it interprets slashes, and inserts its own, and can hide errors
            filename = str(current_user.mcfId) + ext
            paymentFile.save(os.path.join(folder_path, filename))
            
            f = File(filename=filename, filepath=folder_path)
            try:
                db.session.add(f)
                db.session.commit()
            except IntegrityError as i:
                db.session.rollback()
                return redirect(url_for('member_front', whatHappened="Something went wrong: " + i._message()))
                             

            # endfilenamecheck
            return redirect(url_for('member_front', whatHappened="Proof of payment successfully uploaded", paymentProofs=paymentProofs))
        else:
            whatHappened = "Error: File must either be pdf, png or jpeg"
            # endfilenamecheckfail
            return redirect(url_for('member_front', whatHappened=whatHappened))
    else:
        return render_template("login.html", whatHappened = "Session ended")
        # return redirect(url_for('login', whatHappened="Something went wrong: " + i._message()))



    

    


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
    values=[]
    
    for chunk in df:
        app.logger.info("==========")
        # app.logger.info(type(chunk))
        # app.logger.info(chunk)
        app.logger.info("==========")
        
        for index, row in chunk.iterrows():

            if Member.doesUserExist(row[mapFrom['mcfId']]):
                skippedList.append({"mcfId": row[mapFrom['mcfId']]})
                continue


            app.logger.info("%%%%%")
            
            app.logger.info(                
            row[mapFrom['yearOfBirth']]
            )
            # app.logger.info(
            #     convert_nan_to_string(
            #         row[mapFrom['yearOfBirth']]
            #     )
            # )
            app.logger.info("%%%%%")

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

            app.logger.info("==========")
            app.logger.info(values)
            app.logger.info("==========")
            

    if values:
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

    tryRemoveMcfFile("./storage/mcf.csv")                


    return whatHappened, skippedList, newList



   

def processFrlList():
    filename = "frl.csv"
    skippedList = []
    whatHappened = ""
    updatesList = []

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
        app.logger.info(i._message())
        whatHappened = "Something went wrong"
        # return C_templater.custom_render_template("Data entry error", i._message(), False)
        # return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)

    if not whatHappened and not skippedList:
        whatHappened = "PERFECT upload"
    elif not whatHappened and skippedList:
        whatHappened = "Successful upload with details below"


    tryRemoveMcfFile("./storage/frl.csv")                


    return whatHappened, skippedList, updatesList




def updateMcfList():
    filename="mcf.csv"


    mapFrom = C_mapper.excelToDatabase[filename]
    
    wanted_columns = [mapFrom['mcfId'], mapFrom['mcfName'], mapFrom['gender'], mapFrom['yearOfBirth'], mapFrom['state'], mapFrom['nationalRating'], mapFrom['fideId']]


    try:
        df = pd.read_csv(r'./storage/'+filename, usecols=wanted_columns, dtype=str)
    except FileNotFoundError as f:
        return redirect(url_for('main_page', whatHappened="Error: File Not Found, Upload again" ))
        
        





    
    updatesList = []
    failedUpdatesList = []
    # ========== right now skippedList stores ID, which means we can be flexible on how to use it later for more feedback
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
            updatesList.append(row[mapFrom['mcfId']])


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


    tryRemoveMcfFile("./storage/mcf.csv")                
                


    return whatHappened, updatesList, failedUpdatesList, skippedList



def updateFrlList():
    return "mpthing", "nptin"



@app.route('/bulk-process-all-mcf')
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







def allowed_payment_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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

    

@app.route('/bulk-upload-all-files_1', methods=['POST'])
def bulk_upload_all_files_1():


        
    file1 = request.files['file1']


    if file1.filename == '':
        return render_template("main-page.html", whatHappened="There is no file uploaded", whyHappened=[])


    app.logger.info("==========")
    app.logger.info(allowed_bulk_mcf_upload(file1.filename))
    if file1 \
       and allowed_bulk_mcf_upload(file1.filename):
        filename1 = secure_filename(file1.filename)
        file1.save(os.path.join('./storage/mcf.csv'))
        return render_template("main-page.html", whatHappened="MCF file successfully uploaded")
    else:
        whatHappened = "CSV filename must contain mcf.   Eg: mcf-Q1.csv"
        return redirect(url_for('main_page', whatHappened=whatHappened))



    
@app.route('/bulk-upload-all-files_2', methods=['POST'])
def bulk_upload_all_files_2():
        
    file2 = request.files['file2']

    if file2.filename == '':
        return render_template("main-page.html", whatHappened="There is no file uploaded")


    app.logger.info("==========")
    app.logger.info(allowed_bulk_frl_upload(file2.filename))
    if file2 \
       and allowed_bulk_frl_upload(file2.filename):
        filename2 = secure_filename(file2.filename)
        file2.save(os.path.join('./storage/frl.csv'))
        # return 'File successfully uploaded'
        return render_template("main-page.html", whatHappened="FRL file successfully uploaded")
    else:
        whatHappened = "CSV filename must contain frl.   Eg: my-frl-Q4.csv"
        return redirect(url_for('main_page', whatHappened=whatHappened))

@app.route('/display-files-uploaded', methods = ["GET"]) 
def display_files_uploaded():
    # ========== IMPORTANT FOR LATER
    # datetime.date.today().strftime("%d/%m/%Y")
    # ========== IMPORTANT FOR LATER
    fs = db.session.query(File).all()
    # return jsonify(fs)
    app.logger.info(type(fs[0]))
    a_dict = []
    for f in fs:
        a_dict.append({
            "filename": f.filename,
            "filepath": f.filepath,
            "created_at": f.created_at.strftime("%d/%m/%Y")            
        })
    return jsonify(a_dict
        # [i.serialize for i in ]
                   )

    

@app.route('/test-bulk-download') 
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

    # return "nothing burger"
     


if __name__=='__main__': 
    app.run(debug=True)


