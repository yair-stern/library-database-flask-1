from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from flask_cors import CORS
from datetime import datetime, timedelta

# from db_models import Books, Customers, Loans

# import for tests:
import os


app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

class BookTypeEnum(Enum):
    GUIDE = 1  # Maps, dictionaries, technical manuals; 2-day loan  
    FICTION = 2  # Novels, stories, light reading; 5-day loan  
    REFERENCE = 3  # Textbooks, research materials; 10-day loan  

def calculate_loan_duration(book_type):
    """
    Calculate loan duration based on book type.
    """
    return {
        BookTypeEnum.GUIDE: 2,
        BookTypeEnum.FICTION: 5,
        BookTypeEnum.REFERENCE: 10
    }.get(book_type, 0)  # Default to 0 if book type is not found

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
    year_birth = db.Column(db.Integer)
    israel_id = db.Column(db.String(9), nullable=False, unique=True) 

class Loans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False) 
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.now) 
    return_date = db.Column(db.DateTime, default=None)
     # Relationships
    customer = db.relationship("Customers", backref="loans")
    book = db.relationship("Books", backref="loans")

with app.app_context():
    db.create_all()

def unit_test():
    with app.app_context():
        book1 = Books(name="Harry Potter and the Philosopher's Stone", book_type=BookTypeEnum.GUIDE, copies=3, year_published=1997, author="J.K. Rowling")
        book2 = Books(name="The Bible", book_type=BookTypeEnum.GUIDE, copies=1, year_published=-1000, author="Hashem")
        book3 = Books(name="C Programming Language", book_type=BookTypeEnum.GUIDE, copies=1, year_published=1978, author="Brian W. Kernighan, Dennis M. Ritchie")

        book4 = Books(name="The Great Gatsby", book_type=BookTypeEnum.FICTION, copies=2, year_published=1925, author="F. Scott Fitzgerald")
        book5 = Books(name="1984 of Hapyness", book_type=BookTypeEnum.FICTION, copies=2, year_published=1949, author="George Orwell")
        book6 = Books(name="To Kill a Mockingbird", book_type=BookTypeEnum.FICTION, copies=2, year_published=1960, author="Harper Lee")

        book7 = Books(name="Introduction to Algorithms", book_type=BookTypeEnum.REFERENCE, copies=1, year_published=1990, author="Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest")
        book8 = Books(name="The Art of Computer Programming", book_type=BookTypeEnum.REFERENCE, copies=2, year_published=1968, author="Donald E. Knuth")
        book9 = Books(name="The Structure and Interpretation of Computer Programs", book_type=BookTypeEnum.REFERENCE, copies=1, year_published=1985, author="Harold Abelson, Gerald Jay Sussman")

        db.session.add_all([book1, book2, book3, book4, book5, book6, book7, book8, book9])
        db.session.commit()

        customer1 = Customers(name="John Doe", israel_id="123456789")
        customer2 = Customers(name="Jane Smith", israel_id="234567890", city="Haifa", age=25, year_birth=1994)
        customer3 = Customers(name="Alice Johnson", israel_id="345678901", city="Jerusalem", age=40)
        db.session.add_all([customer1, customer2, customer3])
        db.session.commit()

        loan1 = Loans(cust_id=customer1.id, book_id=book1.id)
        loan2 = Loans(cust_id=customer2.id, book_id=book4.id, loan_date=datetime(2025, 1, 10), return_date=datetime(2025, 1, 17))
        loan3 = Loans(cust_id=customer2.id, book_id=book5.id, loan_date=datetime(2025, 1, 9))
        loan4 = Loans(cust_id=customer3.id, book_id=book7.id, loan_date=datetime(2025, 1, 5))
        loan5 = Loans(cust_id=customer3.id, book_id=book8.id, loan_date=datetime(2025, 1, 12, 12, 0))

        db.session.add_all([loan1, loan2, loan3, loan4, loan5])
        db.session.commit()

        print("Test data inserted successfully.")

@app.route("/add_book", methods=["POST"])
def add_book():
    data = request.get_json()
    name = data.get('name')
    book_type = data.get('book_type')
    year_published = data.get('year_published', 5770)
    author = data.get('author', "Unknown")
    copies = data.get('copies', 1)

    if not name or not book_type:
        return jsonify({"message": "Name and book_type are required"}), 400
    
    try:
        book_type = BookTypeEnum.__members__.get(book_type.upper())
    except ValueError:
        return jsonify({"message": "Invalid book_type"}), 400
    
    # Check if the book already exists
    existing_book = Books.query.filter_by(
        name=name,
        year_published=year_published,
        author=author,
        book_type=BookTypeEnum(book_type)
    ).first()

    if existing_book:
        # Update the copies count
        existing_book.copies += copies
        existing_book.copies_in_library += copies
        db.session.commit()
        return jsonify({"message": "Book already exists, updated copies", "id": existing_book.id}), 200
    
    new_book = Books(
        name=name,
        year_published=year_published,
        author=author,
        book_type=book_type,
        copies=copies,
        copies_in_library=copies
    )
    
    db.session.add(new_book)
    db.session.commit()

    return jsonify({"message": "Book added", "id": new_book.id}), 201

@app.route("/add_customers", methods=["POST"])
def add_customer():
    data = request.get_json()
    name = data.get('name')
    israel_id = data.get("israel_id")
    if not israel_id or not name:
         return jsonify({"message": "Name, and israel_id number are required"}), 400
    
    if Customers.query.filter_by(israel_id=israel_id).first():
        # A customer with the same Israel ID as a deleted customer (active = false) cannot be added.
        return jsonify({"message": "A customer with this israel_id already exists"}), 400
    city = data.get('city')
    age = data.get('age')
    if age:
        age = int(age)
    year_birth = data.get('year_birth')
    if year_birth:
        year_birth = int(year_birth)
    if age and not year_birth:
        year_birth = datetime.now().year - age # If the customer hasn't had their birthday yet this year, subtract 1 from their birth year
    new_customrer = Customers(name=name, israel_id=israel_id, city=city, age=age, year_birth=year_birth)

    db.session.add(new_customrer)
    db.session.commit()

    return jsonify({"message": "Customer created", "id": new_customrer.id}), 201

@app.route("/loan_book", methods=["POST"])
def loan_book():
    data = request.get_json()
    book_id = data.get("book_id")
    customer_id = data.get("customer_id")

    if not book_id or not customer_id:
        return jsonify({"message": "Both book_id and customer_id are required"}), 400

    book = Books.query.filter_by(id=book_id, active=True).first()
    if not book:
        return jsonify({"message": "Book not found"}), 404

    if book.copies_in_library < 1:
        return jsonify({"message": "No copies available for loan"}), 400

    customer = Customers.query.filter_by(id=customer_id, active=True).first()
    if not customer:
        return jsonify({"message": "Customer not found or not active"}), 404

    book.copies_in_library -= 1

    loan = Loans(cust_id=customer.id, book_id=book.id)
    db.session.add(loan)

    db.session.commit()

    return jsonify({
        "message": "Book loaned successfully",
        "loan_id": loan.id,
        "book_id": book.id,
        "customer_id": customer.id,
        "loan_date": loan.loan_date.strftime("%Y-%m-%d %H:%M:%S"),
    }), 201

@app.route("/return_book", methods=["POST"])
def return_book():
    data = request.get_json()
    book_id = data.get("book_id")
    customer_id = data.get("customer_id")

    if not book_id or not customer_id:
        return jsonify({"message": "Both book_id and customer_id are required"}), 400

    #Checks if there is an active question
    loan = Loans.query.filter_by(cust_id=customer_id, book_id=book_id, return_date=None).first()
    if not loan:
        return jsonify({"message": "No active loan found for this book and customer"}), 404

    loan.return_date = datetime.now()

    book = Books.query.get(book_id)
    if not book:
        return jsonify({"message": "Book not found"}), 404

    legal_loan_duration = calculate_loan_duration(book.book_type)

    loan_duration = (loan.return_date.date() - loan.loan_date.date()).days
    if loan_duration > legal_loan_duration:
        overdue_message = f"The book was returned {loan_duration-legal_loan_duration} days late."

    # update available copies
    stock_message = None
    if book.active:
        if book.copies_in_library < book.copies:
            book.copies_in_library += 1
        else:
            stock_message = "Error: All copies of this book have already been returned. " \
                 "Please add more copies or check for inconsistencies."
        
    else:
        stock_message = "Error: This book is not active in the library catalog. Please add it."

    db.session.commit()

    response = {
        "message": "Book returned successfully",
        "loan_id": loan.id,
        "book_id": book.id,
        "customer_id": customer_id,
        "return_date": loan.return_date.strftime("%Y-%m-%d %H:%M:%S"),
    }

    if loan_duration > legal_loan_duration:
        response["overdue_message"] = overdue_message
    if stock_message:
        response["error"] = stock_message

    return jsonify(response), 200

@app.route("/books", methods=["GET"])
def display_books():
    books = Books.query.filter_by(active=True).all()
    json_books = [
        {
            "id": book.id,
            "name": book.name,
            "year_published": book.year_published,
            "author": book.author,
            "book_type": book.book_type.name,
            "copies": book.copies,
            "copies_in_library": book.copies_in_library,
        }
        for book in books
    ]
    return jsonify(json_books), 200

@app.route("/customers")
def displey_customers():
    customers = Customers.query.filter_by(active=True).all()
    json_customers = [
            {
                "id": customer.id,
                "name": customer.name,
                "city": customer.city,
                # Calculating age based on year of birth if birth_year exist
                "age": datetime.now().year - customer.year_birth if customer.year_birth else customer.age,
                "israel_id": customer.israel_id
            }
        for customer in customers
    ]
    return jsonify(json_customers), 200

@app.route("/loans")
def display_loans():
    # Retrieving all active loans, those that do not have a return date
    loans = all_loans_details()

    json_loans = []
    for loan in loans:
        # Calculate loan duration based on book type
        legal_loan_duration = calculate_loan_duration(loan.book.book_type)
        # Calculate the due date for the loan
        loan_due_date = loan.loan_date + timedelta(days=legal_loan_duration)

        # Calculate overdue days
        overdue_days = (datetime.now().date() - loan_due_date.date()).days
        # Determine if the loan is on time or late
        on_time = True if overdue_days <= 0 else f"Late by {overdue_days} days"

        json_loans.append({
            "loan_id": loan.id,
            "customer_name": loan.customer.name,
            "customer_id": loan.customer.id,
            "book_name": loan.book.name,
            "book_id": loan.book.id,
            "loan_date": loan.loan_date.strftime("%d-%m-%Y"),
            "due_date": loan_due_date.strftime("%d-%m-%Y"),
            "on_time": on_time
        })

    return jsonify(json_loans), 200

# returns all active loans, and their details, ordered by loan customer name
def all_loans_details():
    return Loans.query.filter_by(return_date=None).join(Customers).join(Books).order_by(Customers.name).all()

@app.route("/late_loans")
def display_late_loans():
    loans = all_loans_details()
    late_loans = []
    for loan in loans:
        # Directly calculates the number of late days without requiring intermediate variables
        days_late = (datetime.now().date() - loan.loan_date.date()).days - calculate_loan_duration(loan.book.book_type)

        if days_late > 0:
            late_loans.append({
                "customer_name": loan.customer.name,
                "book_name": loan.book.name,
                "book_id": loan.book.id,
                "customer_id": loan.customer.id,
                "loan_id": loan.id,
                "loan_date": loan.loan_date.strftime("%d-%m-%Y"),
                "late_days": days_late
            })

    # Sort by late days in descending order
    late_loans_sorted = sorted(late_loans, key=lambda x: x['late_days'], reverse=True)
    return jsonify(late_loans_sorted), 200

# search books by name
@app.route('/search_book', methods=['GET'])
def search_book():
    # Get the name from the query parameter in the url
    book_name = request.args.get('name', '').strip()

    if not book_name:
        return jsonify({"error": "Book name is required"}), 400

    # Query for books with matching name and active=True
    books = Books.query.filter(
        Books.active == True,
        Books.name.ilike(f"%{book_name}%")  # Case-insensitive partial match
    ).all()

    # Prepare JSON response
    json_books = [
        {
            "id": book.id,
            "name": book.name,
            "year_published": book.year_published,
            "author": book.author,
            "book_type": book.book_type.name,  # Enum field as a string
            "copies": book.copies,
            "copies_in_library": book.copies_in_library,
        }
        for book in books
    ]

    return jsonify(json_books), 200

# search customer by name
@app.route('/search_customer', methods=['GET'])
def search_customer():
    # Get the name from the query parameter in the url
    customer_name = request.args.get('name', '').strip()

    if not customer_name:
        return jsonify({"error": "Customer name is required"}), 400

    # customers with matching name and active=True
    customers = Customers.query.filter(
        Customers.active == True,
        Customers.name.ilike(f"%{customer_name}%")  # Case-insensitive partial match
    ).all()

    # Prepare JSON response
    json_customers = [
        {
            "id": customer.id,
                "name": customer.name,
                "city": customer.city,
                # Calculating age based on year of birth if birth_year exist
                "age": datetime.now().year - customer.year_birth if customer.year_birth else customer.age,
                "israel_id": customer.israel_id
        }
        for customer in customers
    ]

    return jsonify(json_customers), 200

# removes copies of a book and returns the results of the deletion
def update_book_copies(book_id, remove_all_copies=False):
    """
    Updates the copies of a book based on the book_id and the remove_all_copies flag.
    If remove_all_copies is True, all copies are removed. Otherwise, one copy is removed.
    Handles only the removal of books available in the library.
    Assumes removing a book decreases an available copy from the library
    """

    if not book_id:
        return {"error": "Book ID is required"}, 400 

    # search in active books
    book = Books.query.filter_by(id=book_id, active=True).first()
    if not book:
        return {"error": "Book not found or not active"}, 404
    
    if remove_all_copies:
        copies_removed = book.copies  # number of the copios
        copies_remaining = 0        
        book.active = False
    else:
        if book.copies <= 0:
            return {"error": "No copies available to remove"}, 400

        copies_removed = 1
        book.copies -= 1
        copies_remaining = book.copies

        if book.copies_in_library > 0:
            book.copies_in_library -= 1

        if book.copies == 0:
            book.active = False

    copies_in_library = 0 if remove_all_copies else book.copies_in_library
            
    db.session.commit()

    return {
        "name": book.name,
        "book_type": book.book_type.name,
        "year_published": book.year_published,
        "author": book.author,
        "copies_removed": copies_removed,
        "copies_remaining": copies_remaining,
        "copies_in_library": copies_in_library,
    }


@app.route("/delete_one_book_copy", methods=["DELETE"])
def delete_one_book_copy():
    book_id = request.args.get("id")
    return update_book_copies(book_id, remove_all_copies=False)

@app.route("/delete_all_book_copies", methods=["DELETE"])
def delete_all_book_copies():
    book_id = request.args.get("id")
    return update_book_copies(book_id, remove_all_copies=True)

# deletes a customer by deactivating
@app.route('/delete_customer', methods=['DELETE'])
def delete_customer():
    customer_id = request.args.get("id")
    if not customer_id:
        return {"error": "Customer ID is required"}, 400

    # search for the customer in the database
    customer = Customers.query.filter_by(id=customer_id, active=True).first()
    if not customer:
        return {"error": "Customer not found or already inactive"}, 404

    # Mark the customer as inactive
    customer.active = False
    db.session.commit()

    return {
        "message": "Customer successfully deleted",
        "customer_name": customer.name,
        "customer_id": customer.id,
        "israel_id": customer.israel_id
    }, 200


if __name__ == "__main__":
    # if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    #     unit_test()
    app.run(debug=True)
