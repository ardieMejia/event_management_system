import logging
from flask import Flask, render_template, request, redirect, jsonify, url_for, Response, make_response, session
# from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
# environment = Environment(loader=FileSystemLoader("templates/"))
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError, DataError
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request, current_user, set_access_cookies, get_jwt
from flask_bcrypt import Bcrypt
from functools import wraps



            

app = Flask(__name__)   # Flask constructor
app.config.from_object(Config)
db = SQLAlchemy(app)

# ===== not sure if we need this app_context, we added after struggling the switch from sqlite to postgresql
with app.app_context():
    db.create_all()

    
migrate = Migrate(app, db, render_as_batch=True)
# app.config['TEMPLATES_AUTO_RELOAD'] = True
jwt = JWTManager(app)
bcrypt = Bcrypt(app)


# Ensure FOREIGN KEY for sqlite3
if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
    def _fk_pragma_on_connect(dbapi_con, con_record):  # noqa
        dbapi_con.execute('pragma foreign_keys=ON')
        
    with app.app_context():
        from sqlalchemy import event
        event.listen(db.engine, 'connect', _fk_pragma_on_connect)



from Models.declarative import EventListing # ===== remove this
import sqlalchemy as sa
app.app_context().push()
from crud import old_Member, old_Event, Crud, Event, Member, Fide


from c_templater import C_templater

# ========== CSV
import csv



# ========== CSV



old_member = old_Member(r"./Members_Data.xlsx","./Used_MembersID.xlsx")
old_event = old_Event(r"./Events_Data.xlsx","./Used_EventsID.xlsx")
crud = Crud()






# def admin_required():
#     def wrapper(fn):
#         @wraps(fn)
#         def decorator(*args, **kwargs):
#             verify_jwt_in_request()
#             claims = get_jwt()
#             if claims["is_administrator"]:
#                 return fn(*args, **kwargs)
#             else:
#                 return jsonify(msg="Admins only!"), 403

#         return decorator

#     return wrapper


  
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



@app.route('/update-single-member', methods = ['POST']) 
def update_single_member():
    # query = sa.select(Member).where(Member.mcfId == mcfId)
    # m = db.session.scalar(query)
    return "new member saved"

    #     m = Member(mcfName = "ardie wiranata", gender='male', yearOfBirth='26-01-1995', state='Selangor', nationalRating='1600')
    #     db.session.add(m)
    #     db.session.commit()
    #     app.logger.info('========== event ==========')
    #     app.logger.info(m)
    #     app.logger.info('========== event ==========')       
#     return "thank you data inserted"

@app.route('/update-fide', methods = ['POST']) 
def update_fide():
    mcfId = request.args.get("mcfId")
    # query = sa.select(Member).where(Member.mcfId == mcfId)
    # m = db.session.scalar(query)
    f = Fide(fideId=request.form['fideId'], fideName=request.form["fideName"], fideRating=request.form['fideRating'], mcfId=request.args.get('mcfId'))
    app.logger.info(f.fideId)
    if f.isDataValid(p_fideId=f.fideId, p_fideRating=f.fideRating):
        errorsList = f.isDataValid(p_fideId=f.fideId, p_fideRating=f.fideRating)
        return C_templater.custom_render_template("Invalid Input Error", errorsList, True)
        

    db.session.add(f)
    try:
        db.session.commit()
    except IntegrityError as i: # ========== exceptions are cool, learn to love exceptions.
        db.session.rollback()
        return C_templater.custom_render_template("Data entry error", i._message, False)
    except DataError as d:
        db.session.rollback()
        return C_templater.custom_render_template("DB API DataError", "this is some basic DB error, nothing special", False)
    
    
    return "new FIDE saved"


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




@app.route('/test2', methods = ['POST']) 
def test2():
    if request.method == 'POST':
        result = old_member.test()
        return result


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
        return C_templater.custom_render_template("Data entry error", i._message, False)
        
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
        return C_templater.custom_render_template("Data entry error", "tournament name duplicate", False)
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
        return C_templater.custom_render_template("Data entry error", i._message, False)
        # example of final form ===== return c_templater("Data entry error", "tournament name duplicate", "error.html")
        
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(old_event.data.values.tolist()))
    app.logger.info(m)
    app.logger.info('========== event ==========')


    return C_templater.custom_render_template("Successfully saved", i._message(), False)




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

    return "event successfully removed"


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

    return "member successfully removed"



@app.route('/events')
# @jwt_required()
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
    access_token = create_access_token(identity="example_user")

    return render_template("events.html", es=es)


@app.route('/members')
# @jwt_required()
def find_members():
    
    query = sa.select(Member)
    # ms = db.session.scalars(query).all()
    ms = db.session.scalars(query).all()
    m = db.session.scalars(query).first()
    # join(Role.users).filter(User.id==cls.user_id).label('user')
    #      return query
    
    
    app.logger.info('========== event ==========')
    app.logger.info(ms)
    app.logger.info('========== event ==========')
    
    # return "wait"
    # ms_dict = [m.__dict__ for m in ms]
    return render_template("members.html", ms=ms)


                    




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
# @jwt_required()
def main_page():

    # access_token = request.args['access_token']  # counterpart for url_for()
    # hidden_data = get_jwt()


    # resp = make_response(render_template("main-page.html"))
    # resp.headers = {'Authorization': 'Bearer {}'.format(access_token)}
    # resp.headers["Content-Type"] = "text/plain"

    return render_template("main-page.html")
    

    # return jsonify(data=hidden_data)

    

@app.route('/test3')
def test3():

    # access_token = request.args['access_token']  # counterpart for url_for()
    # hidden_data = get_jwt()




    # resp = make_response(render_template("main-page.html"))
    # resp.headers = {'Authorization': 'Bearer {}'.format(access_token)}
    # resp.headers["Content-Type"] = "text/plain"

    return render_template("main-page.html")
 
    

    # return jsonify(data=hidden_data)
    
            


    
    



    
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        mcfId = request.form['mcfId']
        password = request.form['password']

        app.logger.info('========== ---------- ++++++++++')
        app.logger.info('Received data:', mcfId , password)
        app.logger.info('========== ---------- ++++++++++')

        m = Member.query.filter_by(mcfId=mcfId).first()
        if m is None:
            return "member ID does NOT exist"
        # isPasswordVerified = bcrypt.check_password_hash(bcrypt.generate_password_hash(password).decode('utf-8'), m.password)
        m.check_password(password)
        if True:    
            return render_template("single-member.html", m=m)
        else:
            return "wrong password"
        # access_token = create_access_token(identity=m.mcfId)

        # session['token'] = 'TOKEN123'  # store token, use it as a dict

        

        # return jsonify(access_token=access_token)

    else:
        return render_template("login.html")
        


@app.route('/bulk-upload-events-csv')
def bulk_upload_events_csv():
    # ========== we upload CSV using the kinda cool declarative_base, might not be good practice for readability
    with open(r'./input/event.csv', newline='') as csvfile:
        dictreader = csv.DictReader(csvfile, delimiter=',')
        for row in dictreader:            
            e = Event(tournamentName=row['tournamentName'], startDate=row['startDate'], endDate=row['endDate'], discipline=row['discipline'])
            db.session.add(e)        
            try:
                db.session.commit()
            except IntegrityError as i:
                db.session.rollback()
                app.logger.info(i._message())
                return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)        


    return C_templater.custom_render_template("Successfull bulk upload", "event data", False)
    # return redirect('/events')


@app.route('/bulk_upload_members_csv')
def bulk_upload_members_csv():
    # ========== we upload CSV using the kinda cool declarative_base, might not be good practice for readability
    with open(r'./input/member.csv', newline='') as csvfile:
        dictreader = csv.DictReader(csvfile, delimiter=',')
        for row in dictreader:
            m = Member(mcfId=row['mcfId'], mcfName=row['mcfName'], gender=row['gender'], yearOfBirth=row['yearOfBirth'], state=row['state'], nationalRating=row['nationalRating'])
            m.set_password(row['password'])

            # query = sa.select(Fide).where(Fide.fideId == row['fideId'])
            # f = db.session.scalar(query)
            # m.fide = f                           
            db.session.add(m)
                
            try:
                db.session.commit()
            except IntegrityError as i:
                db.session.rollback()
                app.logger.info(i._message())
                # return C_templater.custom_render_template("Data entry error", i._message(), False)
                return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)        


    return C_templater.custom_render_template("Successfull bulk upload", "member data", False)


@app.route('/bulk_upload_fide_csv')
def bulk_upload_fide_csv():
    # ========== we upload CSV using the kinda cool declarative_base, might not be good practice for readability
    with open(r'./input/fide.csv', newline='') as csvfile:
        dictreader = csv.DictReader(csvfile, delimiter=',')
        for row in dictreader:
            f = Fide(fideId=row['fideId'], fideName=row['fideName'], fideRating=row['fideRating'], mcfId=row['mcfId'])

            # query = sa.select(Member).where(Member.mcfId == row[''])
            # f = db.session.scalar(query)
            # m.fide = f                           
            db.session.add(f)
                
            try:
                db.session.commit()
            except IntegrityError as i:
                db.session.rollback()
                app.logger.info(i._message())
                # return C_templater.custom_render_template("Data entry error", i._message(), False)
                return C_templater.custom_render_template("DB-API IntegrityError", [i._message()], True)        


    return C_templater.custom_render_template("Successfull bulk upload", "member data", False)

    




if __name__=='__main__': 
    app.run(debug=True)


