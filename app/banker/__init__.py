from flask import Blueprint
from .. import app


banker = Blueprint('banker', __name__, url_prefix='/banker')

from . import views

app.register_blueprint(banker)