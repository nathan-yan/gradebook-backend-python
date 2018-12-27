from pymongo import MongoClient

from . import variables

DATABASE = MongoClient(variables.DB_CONNECTION_STRING)

USERS = DATABASE.Users
CLASSES = DATABASE.Classes