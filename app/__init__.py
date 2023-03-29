from flask import Flask
from .extensions import db


app = Flask(__name__)
app.secret_key = 'super_secret_key'

app.config.from_object('config.Config')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{app.config.get('PG_USER')}:{app.config.get('PG_PASSWORD')}@{app.config.get('PG_HOST')}/{app.config.get('PG_DATABASE')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from . import main
from . import banker
from . import models