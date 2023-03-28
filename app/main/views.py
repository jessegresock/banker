from flask import render_template

from . import main

@main.route('/', methods=['GET'])
def index():
    return render_template('main/home.html')


#@main.route('/banker', methods=['GET'])
#def banker():
#    return render_template('banker/home.html')