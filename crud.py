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
event_member = db.Table(
    "event_members",
    db.Column("event_id", db.ForeignKey("event.id")),
    db.Column("member_id", db.ForeignKey("member.mcfId"))
)

class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    tournamentName = db.Column(db.String(128), index=True, unique=True)
    startDate = db.Column(db.String(64), index=True)
    endDate = db.Column(db.String(64), index=True)
    discipline = db.Column(db.String(64), index=True)
    members = db.relationship('Member', secondary=event_member, back_populates='events')
    def __repr__(self):
        return '<tournament name {tn}> <members {m}>'.format(tn=self.tournamentName, m=self.members)

class Member(UserMixin, db.Model):
    __tablename__ = "member"

    mcfId = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(80))
    mcfName = db.Column(db.String(128), index=True)
    gender = db.Column(db.String(64), index=True)
    yearOfBirth = db.Column(db.String(64), index=True)
    state = db.Column(db.String(64), index=True)
    nationalRating = db.Column(db.String(64), index=True)
    events = db.relationship('Event', secondary=event_member, back_populates='members')
    fideId = db.Column(db.Integer)
    fideName = db.Column(db.String(80))
    fideRating = db.Column(db.Integer(), index=True)


    
    def __repr__(self):
        return '<mcfName {tn}> <events {m}>'.format(tn=self.mcfName, m=self.events)

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
        


    
    @classmethod
    def doesUserExist(cls, id):
        # isPasswordVerified = bcrypt.check_password_hash(self.password, password)
        ret = cls.query.filter_by(mcfId=id).first()
        app.logger.info("++++++++++")
        app.logger.info(ret)
        if ret:
            return True
        return False

    def get_id(self):
        return self.mcfId

    def isDataValid(self, p_fideId, p_fideRating):
        errorsList = []
        if p_fideId.isnumeric() and p_fideRating.isnumeric():
            return True
        if not p_fideId.isnumeric():
            errorsList.append("FIDE ID should be a number")
        if not p_fideRating.isnumeric():
            errorsList.append("FIDE Rating should be a number")
        return errorsList

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


    


    

class old_Event:
    def __init__(self, path, usedID_path):
        print("created event")
        self.path = path
        self.usedID_path = usedID_path
        self.id_field = 'EVENT ID'

                



        # self.id_field = id_field
        # print("created member with path of ", self.path)
        print("used ID is stored at ", self.usedID_path)
        self.data = pd.read_excel(self.path, dtype= 'str')
        self.usedID_data = pd.read_excel(self.usedID_path, dtype= 'str')
        
        
        self.temporary_value = {         # This variable is used for storing our input when using menu create and update
            'EVENT ID': [], 
            'EVENT DATE': [],
            'EVENT FORMAT': [],
            'NUMBER OF ROUNDS': [],
            'COST': []
        }

        




class old_Member:
    def __init__(self, path, usedID_path):
        print("created member")
        self.path = path
        self.usedID_path = usedID_path
        self.id_field = 'MEMBER ID'                



        # self.id_field = id_field
        # print("created member with path of ", self.path)
        print("used ID is stored at ", self.usedID_path)
        self.data = pd.read_excel(self.path, dtype= 'str')
        self.usedID_data = pd.read_excel(self.usedID_path, dtype= 'str')
        
        self.temporary_value = {         # This variable is used for storing our input when using menu create and update
            'MEMBER ID': [],
            'NAME': [],
            'CONTACT NUMBER': [],
            'EMAIL ADDRESS': [],
            'EVENT ID': []
        }

    def test(self):
        return "hahahha spider"


        
                        




class Crud:
    def __init__(self):
        pass


    # Menu Read
    def Show_specific_data(self, model, input_ID):
        
        if input_ID in model.data[model.id_field].values:
            # return model.data.loc[model.data[model.id_field] == input_ID].values
            # pandas dataframe: i think its beautiful, and anyone who disagrees, is hugely mistaken
            return model.data[model.data['EVENT ID'] == input_ID]
        else:
            return None
            

        
    def ID_generator(self,model):        
        id_generator = random.randint(10000,99999)
        
        # ========== later should replace this with model.data[model.id_field]
        all_ids = model.data['MEMBER ID'].tolist() + model.usedID_data['MEMBER ID'].tolist()           
        while id_generator in all_ids:
            # name_length += 1
            # id_generator = f'{DEPARTMENT_initial}{gender}{residence_initial}{name_length}'
            id_generator = random.randint(10000,99999)
            
        model.temporary_value.update({model.id_field: id_generator})


        return id_generator

 
    # Menu Create
    def Input_data_member(self, member):
                
        # global members_path, used_membersID_path
        
        # input_NAME = input('NAME: ').title().strip()
        generated_id = self.ID_generator(member)
        
        member.temporary_value['MEMBER ID'] = generated_id
        member.temporary_value['NAME'] = member.temporary_value['NAME'].title().strip()
        member.temporary_value['CONTACT NUMBER'] = member.temporary_value['CONTACT NUMBER'].title()
        member.temporary_value['EMAIL ADDRESS'] = member.temporary_value['EMAIL ADDRESS'].upper().strip()
        member.temporary_value['EVENT ID'] = member.temporary_value['EVENT ID'].title().strip()
        # input_EMAIL_ADDRESS = input('EMAIL ADDRESS: ').upper().strip()
        # input_EVENT_ID = input('EVENT ID: ').title().strip()



    

        # if self.Input_member_checker(input_NAME, column_input_NAME, parent_model) == True:
        # self.Input_member_checker(input_EVENT_ID, column_input_EVENT, parent_model) == True:
        
        # member.temporary_value.update({'NAME': input_NAME}).title().strip()
        #                 model.temporary_value.update({'CONTACT NUMBER': input_CONTACT_NUMBER})
        #                                 model.temporary_value.update({'EMAIL ADDRESS': input_EMAIL_ADDRESS})
        #                                                 model.temporary_value.update({'EVENT ID': input_EVENT_ID})



        
        
        member.data = pd.concat([member.data, pd.DataFrame.from_dict(member.temporary_value, orient= 'index').T], ignore_index= True)
        
        member.data = member.data.astype(str)
        member.data.to_excel(member.path, index=False)
        


