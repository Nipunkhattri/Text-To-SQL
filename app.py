from flask import Flask
from flask_cors import CORS
from views import blueprint

def create_flask_app(name):
    app = Flask(name)

    app.config.from_object("config.Config")
    CORS(app)

    app.register_blueprint(blueprint)

    return app

app = create_flask_app(__name__)