from flask import Flask, jsonify, request

from gb.api import api

application = Flask(__name__)
application.url_map.strict_slashes = False
application.register_blueprint(api, url_prefix = "/api/v1")

if __name__ == "__main__":
	application.run(port = 5002, debug = True)
