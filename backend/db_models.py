from app import BookTypeEnum
from db_orm import db
from datetime import datetime


class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False) 
    year_published = db.Column(db.Integer, default=5770)
    author = db.Column(db.String(255), default="Unknown")
    book_type = db.Column(db.Enum(BookTypeEnum), nullable=False, default=BookTypeEnum.FICTION)
    active = db.Column(db.Boolean, nullable=False, default=1)
    copies = db.Column(db.Integer, nullable=False, default=1)
    copies_in_library = db.Column(db.Integer, nullable=False, default=1)


class Customers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False) 
    active = db.Column(db.Boolean, nullable=False, default=1) 
    city = db.Column(db.String(255)) 
    age = db.Column(db.Integer)
    year_birth = db.Column(db.Integer)
    israel_id = db.Column(db.String(9), nullable=False) 

class Loans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False) 
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    return_date = db.Column(db.DateTime, default=None)
