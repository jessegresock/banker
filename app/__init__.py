from flask import Flask


app = Flask(__name__)
app.secret_key = 'super_secret_key'

app.config.from_object('config.Config')

from . import main
from . import banker