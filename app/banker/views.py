import csv

from flask import request, render_template, redirect, url_for, flash
from sqlalchemy import create_engine, Table, Column, Integer, String, Date, MetaData, text
import pandas as pd

from . import banker
from .. import app


pg_user = app.config.get('PG_USER')
pg_password = app.config.get('PG_PASSWORD')
pg_host = app.config.get('PG_HOST')
pg_database = app.config.get('PG_DATABASE')

# Configure the database connection
engine = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}/{pg_database}')
#metadata = MetaData()
#testbankdata = Table('testbankdata', metadata,
#    Column('status', String),
#    Column('date', Date),
#    Column('description', String),
#    Column('debit', String),
#    Column('credit', String)
#)


@banker.route('/', methods=['GET'])
def home():
    return render_template('banker/home.html')


@banker.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the uploaded file and save it to disk
        file = request.files['file']
        file.save(file.filename)
        
        # Load the CSV data into a list of dictionaries
        try:
            data = pd.read_csv(file.filename)
            data = data.applymap(lambda x: x.lower() if isinstance(x, str) else x)
            data.columns = data.columns.str.lower()
            data.to_sql('testbankdata', engine, if_exists='append', index=False)
        except Exception as e:
            return "Error inserting the data into table:" + e

        #data = []
        #with open(file.filename, 'r') as f:
        #    csvreader = csv.reader(f)
        #    # Skip header row
        #    next(csvreader)

        #    for line in csvreader:
        #        status, _date, description, debit, credit = line
        #        data.append({'status': status, 'date': _date, 'description': description, 'debit': debit, 'credit': credit})
        
        #try:
        #    # Insert the data into the database
        #    with engine.connect() as conn:
        #        conn.execute(testbankdata.delete())
        #        conn.execute(testbankdata.insert(), data)
        #        conn.commit()
        #except Exception as e:
        #    print("Error inserting the data into table:", e)
        
        # Return a success message to the user
        return redirect('/banker/?success=true')
    
    # Render the file upload form
    return render_template('banker/upload.html')

@banker.route('/view', methods=['GET'])
def view():
    df = pd.read_sql_query(sql=text("SELECT * FROM testbankdata"), con=engine.connect())

    return render_template('banker/view.html', data=df.to_html(index=False))