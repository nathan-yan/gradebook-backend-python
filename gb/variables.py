import os

environment_variables = os.environ

#DB_CONNECTION_STRING = "mongodb://admin:%s@gradebook-cluster0-shard-00-00-l24me.mongodb.net:27017,gradebook-cluster0-shard-00-01-l24me.mongodb.net:27017,gradebook-cluster0-shard-00-02-l24me.mongodb.net:27017/test?ssl=true&replicaSet=GradeBook-Cluster0-shard-0&authSource=admin&retryWrites=true" % environment_variables["GRADEBOOK_DB_PASSWORD"]

DB_CONNECTION_STRING = "mongodb+srv://admin:%s@gradebook-cluster0-l24me.mongodb.net/test?retryWrites=true" % environment_variables['GRADEBOOK_DB_PASSWORD']

BASE_URL = "https://wa-bsd405-psv.edupoint.com/"
