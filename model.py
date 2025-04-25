import unittest
import pandas as pd
from tabulate import tabulate
import random
import os
import sys
import pandas as pd

import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, bcrypt, app, login
from flask_login import UserMixin
from datetime import datetime
import time
from c_mapper import C_mapper
# from sqlalchemy import Column, Table, ForeignKey, Integer, String
# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()
# from sqlalchemy.orm import DeclarativeBase

# Global Variable and Function
# We put our models here, coz the project is kinda small anyway

from sqlalchemy.orm import Mapped, mapped_column, relationship# , declarative_base

# Base = declarative_base()
# engine = create_engine('sqlite:///data.db')

# class Base(DeclarativeBase):
#     pass


# Flask_Login is not "DB aware", so it needs the DBs/app help in this
@login.user_loader
def load_user(id):
    return db.session.get(Member, int(id))

# note for a Core table, we use the sqlalchemy.Column construct,
# not sqlalchemy.orm.mapped_column
# event_member = db.Table(
#     "event_members",
#     db.Column("event_id", db.ForeignKey("event.id")),
#     db.Column("member_id", db.ForeignKey("member.mcfId"))
# )

class Event(db.Model):
    __tablename__ = "events"
    disciplinesList = ["Standard", "Rapid", "Blitz"]

    id = db.Column(db.Integer, primary_key=True)
    tournamentName = db.Column(db.String(128), index=True)
    startDate = db.Column(db.String(64), index=True)
    endDate = db.Column(db.String(64), index=True)
    discipline = db.Column(db.String(64), index=True)
    # members = db.relationship('Member', back_ref='event')

    def set_id(self):
        # acronym = ""
        # for word in self.tournamentName.split():
        #     acronym += word[0].upper()

        return str(int(time.time()))

        
    def __repr__(self):
        return '<tournament name {tn}>'.format(tn=self.tournamentName)

    def isDataInvalid(self, p_tournameName, p_startDate, p_endDate, p_discipline):
        errorsList = []
        if not p_tournameName:
            errorsList.append("Tournament Name should not be empty")
        if not p_startDate:
            errorsList.append("Start Date should not be empty") 
        if not p_endDate:
            errorsList.append("End Date should not be empty")
        app.logger.info("++++++++++")
        app.logger.info(errorsList)
        app.logger.info("++++++++++")
        return errorsList




    

class Member(UserMixin, db.Model):
    __tablename__ = "members"

    mcfId = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(80))
    mcfName = db.Column(db.String(128), index=True)
    gender = db.Column(db.String(64), index=True)
    yearOfBirth = db.Column(db.String(64), index=True)
    state = db.Column(db.String(64), index=True)
    nationalRating = db.Column(db.String(64), index=True)
    # events = db.relationship('Event', secondary=event_member, back_populates='members')
    events = db.Column(db.String(300), index=True)
    fideId = db.Column(db.Integer)
    fideName = db.Column(db.String(80))
    fideRating = db.Column(db.Integer(), index=True)


    
    def __repr__(self):
        return '<mcfName {tn}>'.format(tn=self.mcfName, m=self.events)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # return hashedPassword

    def check_password(self, password):
        # password = password.encode('utf-8')

        isPasswordVerified = bcrypt.check_password_hash(self.password, password)
        return isPasswordVerified
        # app.logger.info(self.password)


    def empty_string_to_zero(num):
        # for those confused
        # the basic shape
        # <statement-to-try> if <return-if-true> else <return-if-else>
        return int(num) if num and num.isdigit() else 0
        
    def getEvents(self):
        return self.events or ""

    
    @classmethod
    def doesUserExist(cls, id):
        # isPasswordVerified = bcrypt.check_password_hash(self.password, password)
        ret = cls.query.filter_by(mcfId=id).first()
        app.logger.info("++++++++++")
        app.logger.info(ret)
        if ret:
            return True
        else:
            return False

    def get_id(self):
        return self.mcfId

    def isDataInvalid(self, p_fideId, p_fideRating):
        errorsList = []
        if p_fideId.isnumeric() and p_fideRating.isnumeric():
            return True
        if not p_fideId.isnumeric():
            errorsList.append("FIDE ID should be a number")
        if not p_fideRating.isnumeric():
            errorsList.append("FIDE Rating should be a number")
        return errorsList



    


    def as_dict_for_file(self,filename):
        mapFrom = C_mapper.excelToDatabase[filename]
        return {
            mapFrom["mcfId"] : self.mcfId, 
            mapFrom["mcfName"] : self.mcfName,
            mapFrom["gender"] : self.gender,
            mapFrom["yearOfBirth"] : self.yearOfBirth,
            mapFrom["state"] : self.state,
            mapFrom["nationalRating"] : self.nationalRating,
            mapFrom["fideId"] : self.fideId,
            mapFrom["events"] : self.events
            # "fideId" : self.fideId,
            # "fideName" : self.fideName,
            # "fideRating" : self.fideRating
        }

                
    def as_dict(self):
        return {
            "mcfId" : self.mcfId, 
            "mcfName" : self.mcfName,
            "gender" : self.gender,
            "yearOfBirth" : self.yearOfBirth,
            "state" : self.state,
            "nationalRating" : self.nationalRating,
            "events" : self.events
            # "fideId" : self.fideId,
            # "fideName" : self.fideName,
            # "fideRating" : self.fideRating
        }

    # @classmethod
    # def doesFideExist(cls, id):
    #     # isPasswordVerified = bcrypt.check_password_hash(self.password, password)
    #     ret = cls.query.filter_by(fideId=id).first()
    #     app.logger.info("++++++++++")
    #     app.logger.info(ret)
    #     if ret:
    #         return True
    #     return False


        


    





    
# class Event(db.Model):
#     id: so.Mapped[int] = so.mapped_column(primary_key=True)
#     tournamentName: so.Mapped[str] = so.mapped_column(sa.String(128), index=True, unique=True)
#     startDate: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
#                                                  unique=False)
#     endDate: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
#                                              unique=False)
#     discipline: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
#                                              unique=False)
#     # eligibility: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
#     #                                          unique=True)
#     # limitation: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
#     #                                          unique=True)
#     # rounds: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
#     #                                          unique=True)
#     # timeControl: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
#     #                                          unique=True)
#     # eventType: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
#     #                                          unique=True)
#     # ageGroup: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
#     #                                          unique=True)
#     # participants: so.Mapped[str] = so.relationship(back_populates='events')

#     def __repr__(self):
#         return '<tournament name {tn}> <start date {sd}>'.format(tn=self.tournamentName, sd=self.startDate)


    








        
                        





        
