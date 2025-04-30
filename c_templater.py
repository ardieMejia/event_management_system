from flask import Flask, render_template, request
import logging
from app import app


c_templatesDict = {
    "DB-API IntegrityError": "database-went-wrong.html",
    "Invalid Input Error": "something-went-wrong.html",
    "DB API DataError": "database-went-wrong.html",
    "Filesize too huge": "database-went-wrong.html",
    "Login Problem": "login-went-wrong.html",
    "Invalid Upload Name": "upload-went-wrong.html"
}

class C_templater:
    def __init__(self):
        pass


    def custom_render_template(errorTopic, errorsList, isTemplate):
        if isTemplate:
            app.logger.info('========== ERROR ==========')
            # app.logger.info(request.form['EVENT ID'])
            # app.logger.info(type(old_event.data.values.tolist()))
            app.logger.info("we render a template here..")
            app.logger.info('========== ERROR ==========')
            return render_template(c_templatesDict[errorTopic], errorTopic=errorTopic, errorsList=errorsList)
        else:
            return '{key} : {value}'.format(key=errorTopic, value=errorsList[0])
            
