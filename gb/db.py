from pymongo import MongoClient

from . import variables

database = MongoClient(variables.DB_CONNECTION_STRING)
