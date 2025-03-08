import logging
from flask import Flask, render_template, request
# from jinja2 import Template
from jinja2 import Environment, FileSystemLoader
environment = Environment(loader=FileSystemLoader("templates/"))

app = Flask(__name__)   # Flask constructor
app.config['TEMPLATES_AUTO_RELOAD'] = True


from crud import Member, Event, Crud

member = Member(r"./Members_Data.xlsx","./Used_MembersID.xlsx")
event = Event(r"./Events_Data.xlsx","./Used_EventsID.xlsx")
crud = Crud()
  
# A decorator used to tell the application 
# which URL is associated function 
@app.route('/form')       
def hello():
    event_s =[
        {'name' : 'ardie'},{'name' : 'what'}
    ]
    app.logger.info('========== event ==========')
    # app.logger.info(request.form['EVENT ID'])
    app.logger.info(type(event.data.values.tolist()))
    app.logger.info(event.data.to_dict('records'))
    app.logger.info('========== event ==========')
    
    
    return render_template("form.html", testvar = "hello", event = event.data.to_dict('records'))



@app.route('/test2', methods = ['POST']) 
def test2():
    if request.method == 'POST':
        result = member.test()
        return result



@app.route('/process_form', methods = ['POST']) 
def process_form():
    if 1 == 0:
        
        if request.method == 'POST':
            member.temporary_value = dict(zip(member.temporary_value, [
                "",
                request.form['NAME'],
                request.form['CONTACT NUMBER'],
                request.form['EMAIL ADDRESS'],
                request.form['EVENT ID']
            ]))
            app.logger.info('==========')
            # app.logger.info(request.form['EVENT ID'])
            app.logger.info(member.temporary_value['EVENT ID'])
            app.logger.info('==========')
            
            result = crud.Input_data_member(member)
            
            # return "hohoho Merry Christmas!!"
            return template.render(result=result)

    return "ahaha"
    
if __name__=='__main__': 
    app.run(debug=True)


