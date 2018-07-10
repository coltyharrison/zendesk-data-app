from flask import Blueprint

data_bp = Blueprint("data", __name__)


@data_bp.route("/get_data")
def get_data():
    return 'OK'
