# library
## Project Overview
This project is a library management system built with Flask and SQLAlchemy. It enables users to manage books, customers, and loan records. The application supports basic CRUD operations, such as adding, updating, deleting, and displaying data for books, customers, and loans.

## Features

1. Books Management
* Add books with properties such as name, publication year, author, type, availability, and copy count.
* Support for three book types (guide, fiction, reference) with predefined loan durations.
2. Customers Management

* Add customers with personal details like name, age, city, year of birth, and unique Israeli ID.

3. Loan Management
* Issue loans to customers, recording loan and return dates.
* Track active loans and return books.

4. API Endpoints

* POST /add_book – Add a new book to the database.
* POST /add_customers – Add a new customer to the database.
* POST /loan_book – Loan a book to a customer.
* POST /return_book – Return a loaned book.
* Additional endpoints for deleting and displaying data.

## decomentation

It is possible to store two books with the same name. Ensure that if they are the same book, they are saved as copies rather than as separate records.
It is possible to add two customers with the same name.
Does not handle errors when a customer borrows multiple copies of the same book or returns a book of which they have multiple copies

Customers have an internal library ID and an Israeli ID. Ensure that no two customers with the same Israeli ID are added.

The default=None setting for return_date indicates that a loan is active until a return date is explicitly set.

Includes a unit test for inserting initial data.
However, it is not complete, as it does not update the number of available copies in the library when creating loan records

## optional:
1. include authors table
2. Describing the active attribute for edge cases:
The active attribute allows loans to be marked as deleted, but it is not recommended to use this; instead, books should be returned properly. This attribute is intended for extreme cases and will prompt librarians with a confirmation message to ensure their action is intentional.

### Design Choice: DAL Implementation

For this project, I chose to implement the Data Access Layer (DAL) using standalone functions instead of integrating them within object-oriented classes. This approach simplifies the structure and makes the code more straightforward to work with, given the small scope and relatively simple requirements of the project.  

If the project evolves or requires more complexity in the future, transitioning to a fully object-oriented design with methods inside dedicated classes can be considered.

## working:
Client-side, handling error when adding a customer.