from flask import Blueprint
from flask_restx import Api
from config import Config
from views.connect_api import connect_api

blueprint = Blueprint("api", "flask backend")
api = Api(blueprint, title='Apis', version='1.0', docs=Config.DEBUG)

api.add_namespace(connect_api)