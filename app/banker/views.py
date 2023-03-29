import csv
import datetime

from flask import request, render_template, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, Table, Column, Integer, String, Date, MetaData, text
from sqlalchemy.orm import sessionmaker
from io import StringIO 
import pandas as pd

from . import banker
from .. import app
from ..extensions import db
from ..models import CitiTransactionData
from . import categorizer


## Configure the database connection
engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

@banker.route('/', methods=['GET'])
def home():
    # get date data for last month
    today = datetime.date.today()
    last_month_end = datetime.date(today.year, today.month, 1) - datetime.timedelta(days=1)
    last_month_start = datetime.date(last_month_end.year, last_month_end.month, 1)

    # get all database transaction data and filter for last month
    postgres_df = pd.read_sql_query(sql=text("SELECT * FROM citi_transaction_data"), con=engine.connect())
    postgres_df = postgres_df[(postgres_df['date'] >= last_month_start) & (postgres_df['date'] <= last_month_end)]

    # place into dataframes for processing
    gas_df = postgres_df[postgres_df['category'] == 'gas']
    grocery_df = postgres_df[postgres_df['category'] == 'grocery']
    entertainment_df = postgres_df[postgres_df['category'] == 'entertainment']
    other_df = postgres_df[postgres_df['category'] == 'uncategorized']

    # agg across each dataframe
    agg_gas_df = gas_df.groupby('category').agg({'debit': 'sum'})
    agg_grocery_df = grocery_df.groupby('category').agg({'debit': 'sum'})
    agg_entertainment_df = entertainment_df.groupby('category').agg({'debit': 'sum'})
    agg_other_df = other_df.groupby('category').agg({'debit': 'sum'})

    # get aggregate value, if empty return 0
    gas_agg = agg_gas_df.values.tolist()[0][0] if not agg_gas_df.empty else 0
    grocery_agg = agg_grocery_df.values.tolist()[0][0] if not agg_grocery_df.empty else 0
    entertainment_agg = agg_entertainment_df.values.tolist()[0][0] if not agg_entertainment_df.empty else 0
    other_agg = agg_other_df.values.tolist()[0][0] if not agg_other_df.empty else 0

    render_context = {
        'gas_data': '$'+ str(round(gas_agg, 2)),
        'grocery_data': '$' + str(round(grocery_agg, 2)),
        'entertainment_data': '$'+ str(round(entertainment_agg, 2)),
        'other_data': '$'+ str(round(other_agg, 2)),
        'today': today,
        'month_end':last_month_end,
    }

    return render_template('banker/home.html', **render_context) 


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
            data = categorizer.apply_category(data)

            for index, row in data.iterrows():
                transaction = CitiTransactionData(
                    status=row['status'],
                    date=row['date'],
                    description=row['description'],
                    debit=row['debit'],
                    credit=row['credit'],
                    category=row['category']
                )
                db.session.add(transaction)

            db.session.commit()
        except Exception as e:
            return "Error inserting the data into table:" + e

        # Return a success message to the user
        return redirect('/banker/?success=true')
    
    # Render the file upload form
    return render_template('banker/upload.html')


@banker.route('/view', methods=['GET'])
def view():
    data = CitiTransactionData.query.all()
    return render_template('banker/view.html', data=data)


@banker.route('/update_row/<int:id>', methods=['POST'])
def update_row(id):
    row = CitiTransactionData.query.filter_by(id=id).first()
    row.status = request.form['status']
    row.date = request.form['date']
    row.description = request.form['description']
    row.debit = request.form['debit']
    row.credit = request.form['credit']
    row.created_at = request.form['created_at']
    row.category = request.form['category']
    db.session.commit()
    return redirect(url_for('banker.view'))