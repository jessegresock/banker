from flask import Blueprint
from .. import app


main = Blueprint('main', __name__,)

from . import views

app.register_blueprint(main)