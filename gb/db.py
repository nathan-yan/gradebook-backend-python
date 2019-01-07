from pymongo import MongoClient

from . import variables

connection = MongoClient(variables.DB_CONNECTION_STRING)
GRADEBOOK = connection['gradebook-primary']

USERS = GRADEBOOK.Users
CLASSES = GRADEBOOK.Classes
SESSIONS = GRADEBOOK.Sessions
API_KEYS = GRADEBOOK.Keys