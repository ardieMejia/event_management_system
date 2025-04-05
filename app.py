import logging
from flask import Flask, render_template, request, redirect, url_for
# from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
# environment = Environment(loader=FileSystemLoader("templates/"))
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_paginate import Pagination, get_page_args
from werkzeug.utils import secure_filename
import os
import time
import pandas as pd

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
from crud import old_Member, old_Event, Crud, Event, Member


from c_templater import C_templater

# ========== CSV
import csv


# ========== CSV


old_member = old_Member(r"./Members_Data.xlsx","./Used_MembersID.xlsx")
old_event = old_Event(r"./Events_Data.xlsx","./Used_EventsID.xlsx")
crud = Crud()
from c_mapper import C_mapper

start=0
end=0


    
# A decorator used to tell the application 
# which URL is associated function 
@app.route('/form')       
def hello():
    event_s =[
        {'name' : 'ardie'},{'name' : 'what'}
    ]
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    app.logger.info(type(old_event.data.values.tolist()))
    app.logger.info(old_event.data.to_dict('records'))
    app.logger.info('========== event ==========')
    
    
    return render_template("form.html", testvar = "hello", old_event = old_event.data.to_dict('records'))



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
    if not m.isDataValid(p_fideId=m.fideId, p_fideRating=m.fideRating):
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
        return C_templater.custom_render_template(errorTopic="DB API DataError", errorsList=[i._message], isTemplate=True)


    
    # return "new FIDE saved"
    return render_template("single-member.html", m=m, whatHappened="new FIDE saved")

@app.route('/event-create')
def event_create():
    app.logger.info('========== event ==========')
    app.logger.info('========== event ==========')
    
    return render_template("event-create.html")

# @app.route('/member-create')
# def member_create():
#     app.logger.info('========== member ==========')
#     app.logger.info('========== member ==========')
    
#     return render_template("member-create.html")




# @app.route('/test2', methods = ['POST']) 
# def test2():
#     if request.method == 'POST':
#         result = old_member.test()
#         return result


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
    
    m = db.session.query(Member).get(request.form['mcfId'])
    e = db.session.query(Event).get(request.form['events'])
    
    m.events.append(e)
    e.members.append(m)    
    
    try:
        db.session.commit()
    except IntegrityError as i:
        db.session.rollback()
        return C_templater.custom_render_template(errorTopic="DB-API IntegrityError", errorsList=[i._message], isTemplate=True)
    
    app.logger.info('========== event ==========')
    app.logger.info('========== event ==========')

    return "update successfully"


@app.route('/create-event', methods = ['POST']) 
def create_event():                
    e = Event(tournamentName=request.form['tournamentName'], startDate=request.form['startDate'], endDate=request.form['endDate'], discipline=request.form['discipline'])
    
    db.session.add(e)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return C_templater.custom_render_template(errorTopic="DB-API IntegrityError", errorsList=[i._message], isTemplate=True)
    # this ones good ===== return c_templater("Data entry error", "tournament name duplicate", "error.html")
        
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))
    app.logger.info(e)
    app.logger.info('========== event ==========')

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

    query = sa.select(Event)
    es = db.session.scalars(query).all()

    
    
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))
    app.logger.info(es)
    app.logger.info('========== event ==========')

    return render_template("events.html", es=es)


@app.route('/members') 
def find_members():

    page = request.args.get("page", 1, type=int)
    
    query = sa.select(Member)
    ms_paginate=db.paginate(query, page=page, per_page=20, error_out=False)
    # ms = db.session.scalars(query).all()

    # prev_url = "a_page/page=23"
    prev_url = url_for("find_members", page=ms_paginate.prev_num)
    next_url = url_for("find_members", page=ms_paginate.next_num)


    app.logger.info('========== event ==========')
    app.logger.info(ms_paginate)
    app.logger.info('========== event ==========')
    
    # return "wait"
    # ms_dict = [m.__dict__ for m in ms]
    return render_template("members.html", ms=ms_paginate.items, prev_url=prev_url, next_url=next_url, page=page, totalPages=ms_paginate.total)

                    




@app.route('/process_form', methods = ['POST']) 
def process_form():
    if 1 == 1:
        
        if request.method == 'POST':
            old_member.temporary_value = dict(zip(old_member.temporary_value, [
                "",
                request.form['NAME'],
                request.form['CONTACT NUMBER'],
                request.form['EMAIL ADDRESS'],
                request.form['EVENT ID']
            ]))
            app.logger.info('==========')
            # app.logger.info(request.form['EVENT ID'])
            app.logger.info(old_member.temporary_value['EVENT ID'])
            app.logger.info('==========')
            
            result = crud.Input_data_member(old_member)
            
            # return "hohoho Merry Christmas!!"
            return template.render(result=result)

                    

    return "ahaha"

@app.route('/ajax', methods = ['POST','GET']) 
def ajax_get_event():

    specific_data = crud.Show_specific_data(old_event, request.args.get('event_id'))
    app.logger.info('========== ---------- ++++++++++')
    # app.logger.info(request.args.get('event-id'))
    app.logger.info(specific_data['EVENT NAME'].values[0])
    # app.logger.info(specific_data['EVENT NAME'])
    # app.logger.info(type(request.args))
    app.logger.info('========== ---------- ++++++++++')
    

    return {
        # 'event_id': request.args.get('event_id')
        'event_date': specific_data['EVENT DATE'].values[0],
        'event_format': specific_data['EVENT FORMAT'].values[0],
        'no_of_rounds': specific_data['NUMBER OF ROUNDS'].values[0],
        'gender': specific_data['GENDER'].values[0],
        'cat': specific_data['CATEGORY'].values[0],
        'subcat': specific_data['SUB CATEGORY'].values[0],
        'cost': specific_data['COST'].values[0]

        
        # 'asd': asdsad,
        # 'asd'
        # <div id="event-date" ></div>
	# <div id="event-format" ></div>
	# <div id="no-of-rounds" ></div>
	# <div id="gender" ></div>
	# <div id="cat" ></div>
	# <div id="subcat" ></div>
	# <div id="cost" ></div>
    }

                    



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
            login_user(m)
            return render_template("single-member.html", m=m)

        
        # access_token = create_access_token(identity=m.mcfId)

        # session['token'] = 'TOKEN123'  # store token, use it as a dict

        # return jsonify(access_token=access_token)

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
                      
                      
    df = pd.read_csv(r'./storage/'+filename, usecols=wanted_columns)
                           

    values=[]
    df = df.astype(str)
    for index, row in df.iterrows():

        values.append(
            {
            "mcfId": row[mapFrom['mcfId']],
            "mcfName": row[mapFrom['mcfName']],
            "gender": row[mapFrom['gender']],
            "yearOfBirth": row[mapFrom['yearOfBirth']],
            "state": row[mapFrom['state']],
            "nationalRating": row[mapFrom['nationalRating']],
            "fideId": Member.empty_string_to_zero(num = row[mapFrom['fideId']]),
            "password": bcrypt.generate_password_hash(row[mapFrom['password']]).decode('utf-8')
            }
        )


            
        # if not m.doesUserExist(m.mcfId):
        #     db.session.add(m)
        #     db.session.add(f)
        # else:
        #     duplicatesList.append(m)
        

        # ===== try uploading bulk

    statement = db.insert(Member)
    db.session.execute(statement, values)


    
    try:
        db.session.commit()

    except IntegrityError as i:
        db.session.rollback()
        app.logger.info(i._message())
        # return C_templater.custom_render_template("Data entry error", i._message(), False)
        return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)





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





@app.route('/bulk-process-all-members')
def bulk_process_all_members():
    start = time.time()
    processMcfList()
    whatHappened, whyHappened = processFideList()
    end = time.time()
    length = end - start
    app.logger.info("\\\\\\\\\\\\\\\\\\\\")
    app.logger.info(length)
    app.logger.info("\\\\\\\\\\\\\\\\\\\\")


    return render_template("main-page.html", whatHappened=whatHappened, whyHappened=whyHappened)
    



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def allowed_bulk_upload(filename):
    return "mcf.csv" in filename.lower() or "frl.csv" in filename.lower()
    # return '.' in filename and \
    #        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/bulk-upload-all-files', methods=['POST'])
def bulk_upload_all_files():

    
    # app.logger.info("==========")
    # app.logger.info(request.files)
    
    # if 'file' not in request.files:
        # return redirect(request.url)
        
    file1 = request.files['file1']
    file2 = request.files['file2']

    if file1.filename == '' or file2.filename == '':
        return render_template("main-page.html", whatHappened="File must be named mcf.csv and frl.csv", whyHappened=[])


    app.logger.info("==========")
    app.logger.info(allowed_bulk_upload(file1.filename))
    app.logger.info(allowed_bulk_upload(file2.filename))
    if file1 and file2 \
       and allowed_bulk_upload(file1.filename) \
       and allowed_bulk_upload(file2.filename):
        filename1 = secure_filename(file1.filename)
        file1.save(os.path.join('./storage/', filename1.lower()))
        filename2 = secure_filename(file2.filename)
        file2.save(os.path.join('./storage/', filename2.lower()))
        # return 'File successfully uploaded'
        return render_template("main-page.html", whatHappened="Both files successfully uploaded")
    else:
        return C_templater.custom_render_template("Invalid Upload Name", [format(app.config['ALLOWED_EXTENSIONS']), "files must be named either mcf.csv or frl.csv"], True)
        # return 'Invalid file type'
    # return "wait"


if __name__=='__main__': 
    app.run(debug=True)


