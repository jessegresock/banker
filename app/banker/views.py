import csv

from flask import request, render_template, redirect, url_for, flash
from sqlalchemy import create_engine, Table, Column, Integer, String, Date, MetaData, text
from io import StringIO 
import pandas as pd

from . import banker
from .. import app


# Get Postgres database connection details
pg_user = app.config.get('PG_USER')
pg_password = app.config.get('PG_PASSWORD')
pg_host = app.config.get('PG_HOST')
pg_database = app.config.get('PG_DATABASE')

# Configure the database connection
engine = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}/{pg_database}')


@banker.route('/', methods=['GET'])
def home():
    return render_template('banker/home.html')


@banker.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the uploaded file and save it to disk
        filedata = request.files['file'].read()
        string_data = filedata.decode('utf-8')
        
        # Load the CSV data into a list of dictionaries
        try:
            data = pd.read_csv(StringIO(string_data))
            data = data.applymap(lambda x: x.lower() if isinstance(x, str) else x)
            data.columns = data.columns.str.lower()
            data.to_sql('testbankdata', engine, if_exists='append', index=False)
        except Exception as e:
            return "Error inserting the data into table:" + e

        # Return a success message to the user
        return redirect('/banker/?success=true')
    
    # Render the file upload form
    return render_template('banker/upload.html')


@banker.route('/view', methods=['GET'])
def view():
    df = pd.read_sql_query(sql=text("SELECT * FROM testbankdata"), con=engine.connect())

    return render_template('banker/view.html', data=df.to_html(index=False))