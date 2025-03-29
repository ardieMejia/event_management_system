# Excel-Based-Event-Registration-Management-Python-CRUD-Application
This project is a CRUD (Create, Read, Update, Delete) application for a client. It started out using Excel as its database, originally based on the repo https://github.com/AnthonyDjogan/Excel-Based-Employee-Management-System_Python-CRUD-Application. The instructions for usage are pretty much the same. Simplified instructions below. 

---
Most importantly:
  1. In the code, modify the values of 'employee_path', 'dept_path', and 'usedID_path' to the appropriate file paths on your local machine where you want to store the data
  
  The code is the (bad) documentation, so we are writing app behaviour here
For running our app:
  1. run flask --app main.py run --debug --extra-files "templates/form.html:crud.py:main.py"
Cascade deletes for our ORM, so that means:
  1. deleting members details will also delete FIDE details
  



