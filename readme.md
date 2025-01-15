# library
## decomentation
needs to include CRUD - nut yet
Note on relationship in SQLAlchemy:
Learning how to use db.relationship simplifies working with related data in models. It allows bidirectional access to related records and simplifies queries, improving the readability and efficiency of the code.

It is possible to store two books with the same title. Ensure that if they are the same book, they are saved as copies rather than as separate records.

Customers have an internal library ID and an Israeli ID. Ensure that no two customers with the same Israeli ID are added.

The default=None setting for return_date indicates that a loan is active until a return date is explicitly set.

## optional:
1. include authors table
2. Describing the active attribute for edge cases:
The active attribute allows loans to be marked as deleted, but it is not recommended to use this; instead, books should be returned properly. This attribute is intended for extreme cases and will prompt librarians with a confirmation message to ensure their action is intentional.
3. Note on relationship in SQLAlchemy:
Learning how to use db.relationship simplifies working with related data in models. It allows bidirectional access to related records and simplifies queries, improving the readability and efficiency of the code.
## working:
1. configure database: 
    save to git
    create unit test
    try to save data to db