import logging
from flask import Flask, render_template, request
# from jinja2 import Template
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from jinja2 import Environment, FileSystemLoader
environment = Environment(loader=FileSystemLoader("templates/"))
import sqlalchemy as sa

app = Flask(__name__)   # Flask constructor
app.template_folder = r'./templates/'
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.app_context().push()

from crud import Member, Event, Crud, User, Post

member = Member(r"./Members_Data.xlsx","./Used_MembersID.xlsx")
event = Event(r"./Events_Data.xlsx","./Used_EventsID.xlsx")
crud = Crud()

u = User(username='susan', email='susan@example.com')
  
# A decorator used to tell the application 
# which URL is associated function 
@app.route('/form')       
def hello():
    event_s =[
        {'name' : 'ardie'},{'name' : 'what'}
    ]
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    # app.logger.info(type(event.data.values.tolist()))
    # app.logger.info(event.data.to_dict('records'))
    app.logger.info(dir(app))
    app.logger.info(type(db))
    app.logger.info(type(migrate))
    app.logger.info('========== event ==========')

    
    query = sa.select(User)
    db.session.scalars(query).all()


    users = db.session.scalars(query)

    # for u in users:
    #     print(u.id, u.username)
    
    
    return render_template("form.html", testvar = "hello", event = event.data.to_dict('records'), users=users)





@app.route('/test2', methods = ['POST']) 
def test2():
    if request.method == 'POST':
        result = member.test()
        return result



@app.route('/process_form', methods = ['POST']) 
def process_form():
    if 1 == 1:
        
        if request.method == 'POST':
            member.temporary_value = dict(zip(member.temporary_value, [
                "",
                request.form['NAME'],
                request.form['CONTACT NUMBER'],
                request.form['EMAIL ADDRESS'],
                request.form['EVENT ID']
            ]))
            app.logger.info('==========')
            app.logger.info(member.temporary_value['EVENT ID'])
            app.logger.info('==========')
            
            result = crud.Input_data_member(member)
            member.temporary_value = {         # This variable is used for storing our input when using menu create and update
                'MEMBER ID': member.temporary_value['MEMBER ID'], 
                'NAME': member.temporary_value['NAME'],
                'CONTACT NUMBER': member.temporary_value['CONTACT NUMBER'],
                'EMAIL ADDRESS': member.temporary_value['EMAIL ADDRESS'],
                'EVENT ID': member.temporary_value['EVENT ID']
            }


            specific_event = crud.Show_specific_data(event, member.temporary_value['EVENT ID'])


            registered_event = {
                'event_id': specific_event
                # 'event_date': specific_event['EVENT DATE'].values,
                # 'event_format': specific_event['EVENT FORMAT'].values[0],
                # 'no_of_rounds': specific_event['NUMBER OF ROUNDS'].values[0],
                # 'gender': specific_event['GENDER'].values[0],
                # 'cat': specific_event['CATEGORY'].values[0],
                # 'subcat': specific_event['SUB CATEGORY'].values[0]
            }
            # return "hohoho Merry Christmas!!"
            # return template.render(result=result)
            return render_template("thanks.html", a_member = member.temporary_value)# , testvar = "hello", event = event.data.to_dict('records'))


                    

    return "ahaha"


@app.route('/write_post', methods = ['POST']) 
def write_post():

        
    if request.method == 'POST':
        # member.temporary_value = dict(zip(member.temporary_value, [
        #     "",
        #     request.form['username'],
        #     request.form['email'],
        #     request.form['EMAIL ADDRESS'],
        #     request.form['EVENT ID']
        # ]))
        app.logger.info('==========')
        app.logger.info(request.form)
        app.logger.info(request.form['user_id'])
        app.logger.info('==========')

        # u = db.session.get(User, request.form['user_id'])        

        # return "test"
        

        

        # u = db.session.get(User, request.form['u'])
        

        return render_template("post_form.html", u_id = request.form['user_id'])# , testvar = "hello", event = event.data.to_dict('records'))

@app.route('/great_post_done', methods = ['POST']) 
def great_post_done():

        
    if request.method == 'POST':
        # member.temporary_value = dict(zip(member.temporary_value, [
        #     "",
        #     request.form['username'],
        #     request.form['email'],
        #     request.form['EMAIL ADDRESS'],
        #     request.form['EVENT ID']
        # ]))
        app.logger.info('==========')
        app.logger.info(request.form)
        app.logger.info(request.form['body'])
        app.logger.info(request.form['u_id'])
        app.logger.info('==========')

        # return "aa"

        

        u = db.session.get(User, request.form['u_id'])
        p = Post(body=request.form['body'], author=u)

        db.session.add(p)
        db.session.commit()

        return render_template("great_post_done_ack.html", p = p)# , testvar = "hello", event = event.data.to_dict('records'))

    
    
@app.route('/process_user', methods = ['POST']) 
def process_user():

        
    if request.method == 'POST':
        # member.temporary_value = dict(zip(member.temporary_value, [
        #     "",
        #     request.form['username'],
        #     request.form['email'],
        #     request.form['EMAIL ADDRESS'],
        #     request.form['EVENT ID']
        # ]))
        app.logger.info('==========')
        app.logger.info(request.form)
        app.logger.info(request.form['username'])
        app.logger.info('==========')


        u = User(username=request.form['username'], email=request.form['email'])
        db.session.add(u)
        db.session.commit()
        
        return "registraion of user complete"

        # u = db.session.get(User, request.form['id'])
        

        # return render_template("post_form.html", u = u)# , testvar = "hello", event = event.data.to_dict('records'))


        


@app.route('/ajax', methods = ['POST','GET']) 
def ajax_get_event():

    specific_data = crud.Show_specific_data(event, request.args.get('event_id'))
    app.logger.info('========== ---------- ++++++++++')
    # app.logger.info(request.args.get('event-id'))
    app.logger.info(specific_data['EVENT NAME'].values[0])
    # app.logger.info(specific_data['EVENT NAME'])
    # app.logger.info(type(request.args))
    app.logger.info('========== ---------- ++++++++++')
    

    return {
        'event_id': specific_data['EVENT ID'].values[0],
        'event_date': specific_data['EVENT DATE'].values[0],
        'event_format': specific_data['EVENT FORMAT'].values[0],
        'no_of_rounds': specific_data['NUMBER OF ROUNDS'].values[0],
        'gender': specific_data['GENDER'].values[0],
        'cat': specific_data['CATEGORY'].values[0],
        'subcat': specific_data['SUB CATEGORY'].values[0],
        'cost': specific_data['COST'].values[0]

        
    }

                    




if __name__=='__main__': 
    app.run()


