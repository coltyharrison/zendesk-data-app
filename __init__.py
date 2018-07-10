from logging.config import dictConfig

from data.views import data_bp
from flask import Flask, render_template


def create_app():
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })
    app = Flask(__name__)
    app.register_blueprint(data_bp, url_prefix="/data")

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
