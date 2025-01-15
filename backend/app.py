from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class BookTypeEnum(Enum):
    GUIDE = 1  # Maps, dictionaries, technical manuals; 2-day loan  
    FICTION = 2  # Novels, stories, light reading; 5-day loan  
    REFERENCE = 3  # Textbooks, research materials; 10-day loan  

db = SQLAlchemy(app)

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
    israel_id = db.Column(db.String(9), nullable=False) 

class Loans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False) 
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    return_date = db.Column(db.DateTime, default=None)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    customers = Customers.query.all()
    return {"customers": [customer.id for customer in customers]}

if __name__=="__main__":
    app.run(debug=True)

