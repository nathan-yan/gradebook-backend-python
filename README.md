# GradeBook
GradeBook is a Synergy StudentVUE interface that offers a modern UI and useful features for students, such as projected grade calculation and graphical interpretations of grade through time. GradeBook aims to improve the look and experience of StudentVUE.

GradeBook's backend is currently hosted on a DigitalOcean droplet. We use HTTPS and HSTS to ensure that all information between the users' computer and Synergy's servers is encrypted.

This repository in particular is the backend of GradeBook, written in Python for fast development.

## Dependencies
1. Flask == 0.10.1
2. itsdangerous == 0.24
3. Werkzeug == 0.10.1
4. requests >= 2.18
5. beautifulsoup4 >= 4.3.0
6. pymongo == 3.6.0
7. dnspython == ??

GradeBook uses MongoDB as its database to store persistent user metadata. Obviously, any one who forks this repository either to contribute or to modify for their own purposes will not have access to the primary GradeBook database, but anyone can create a free Monogo database locally or in the cloud using MongoDB Atlas.

If the MongoDB is hosted in the cloud, you'll need to copy your connection string to gb/db.py. Then set your DB credentials as an environment variable.

`export GRADEBOOK_DB_PASSWORD=[CREDENTIAL]`

If you're using Windows, replace the "export" with "set" 

## How to Run
GradeBook is a Flask application in Python. Once the repository has been cloned, navigate into the repository and install dependencies using

`pip install -r requirements.txt`

You can then run the application by typing these lines into the console

```export FLASK_APP=application.py
export FLASK_DEBUG=1
flask run --host=A.B.C.D --port=PORT
```
