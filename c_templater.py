from flask import Flask, render_template, request
import logging
from app import app


class C_templater:
    def __init__(self):
        pass


    def custom_render_template(error_sentence_1, error_sentence_2, *args):
        if len(args) == 0:
            return '{key} : {value}'.format(key=error_sentence_1, value=error_sentence_2)
        else:
            app.logger.info('========== ERROR ==========')
            # app.logger.info(request.form['EVENT ID'])
            # app.logger.info(type(old_event.data.values.tolist()))
            app.logger.info("we render a template here..")
            app.logger.info('========== ERROR ==========')
            return "template should be here"
            
