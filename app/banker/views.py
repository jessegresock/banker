import csv
from datetime import datetime, date, timedelta

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
from . import webobjs


## Configure the database connection
engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

@banker.route('/', methods=['GET'])
def home():
    # get date data for last month
    today = date.today()
    last_month_end = date(today.year, today.month, 1) - timedelta(days=1)
    last_month_start = date(last_month_end.year, last_month_end.month, 1)

    # get all database transaction data and filter for last month
    postgres_df = pd.read_sql_query(sql=text("SELECT * FROM citi_transaction_data"), con=engine.connect())
    postgres_df = postgres_df[(postgres_df['date'] >= last_month_start) & (postgres_df['date'] <= last_month_end)]

    # get aggregate value, if empty return 0
    gas_agg = get_category_agg('gas', postgres_df)
    grocery_agg = get_category_agg('grocery', postgres_df)
    entertainment_agg = get_category_agg('entertainment', postgres_df)
    other_agg = get_category_agg('house', postgres_df)

    # TODO: THIS NEEDS TO BE FIXED
    tiles = [
        webobjs.DataTile('$' + str(round(gas_agg, 2)), 'Gas'),
        webobjs.DataTile('$' + str(round(grocery_agg, 2)), 'Grocery'),
        webobjs.DataTile('$' + str(round(entertainment_agg, 2)), 'Entertainment'),
        webobjs.DataTile('$' + str(round(other_agg, 2)), 'House'),
    ]

    render_context = {
        'gas_data': '$'+ str(round(gas_agg, 2)),
        'grocery_data': '$' + str(round(grocery_agg, 2)),
        'entertainment_data': '$'+ str(round(entertainment_agg, 2)),
        'other_data': '$'+ str(round(other_agg, 2)),
        'today': today,
        'month_end':last_month_end,
    }

    return render_template('banker/home.html', today=today, month_end=last_month_end, tiles=tiles) 


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
    data = CitiTransactionData.query.order_by(CitiTransactionData.date.desc()).all()
    return render_template('banker/view.html', data=data)


@banker.route('/update_row/<int:id>', methods=['POST'])
def update_row(id):
    row = CitiTransactionData.query.filter_by(id=id).first()
    row.category = request.form['category']
    db.session.commit()
    return redirect(url_for('banker.view'))


@banker.route('/insights', methods=['GET', 'POST'])
def insights():
    if request.method == 'POST':
        week_start = datetime.strptime(request.form['dropdown'], '%Y-%m-%d').date()
        week_end = (week_start + timedelta(days=week_start.weekday()))

        # get all database transaction data and filter for last month
        postgres_df = pd.read_sql_query(sql=text("SELECT * FROM citi_transaction_data"), con=engine.connect())
        postgres_df = postgres_df[(postgres_df['date'] >= week_start) & (postgres_df['date'] <= week_end)]

        # get aggregate value, if empty return 0
        gas_agg = get_category_agg('gas', postgres_df)
        grocery_agg = get_category_agg('grocery', postgres_df)
        entertainment_agg = get_category_agg('entertainment', postgres_df)
        other_agg = get_category_agg('house', postgres_df)

        render_context = {
            'gas_data': '$'+ str(round(gas_agg, 2)),
            'grocery_data': '$' + str(round(grocery_agg, 2)),
            'entertainment_data': '$'+ str(round(entertainment_agg, 2)),
            'other_data': '$'+ str(round(other_agg, 2)),
            'week_start': week_start
        }

        tiles = [
            webobjs.DataTile('$' + str(round(gas_agg, 2)), 'Gas'),
            webobjs.DataTile('$' + str(round(grocery_agg, 2)), 'Grocery'),
            webobjs.DataTile('$' + str(round(entertainment_agg, 2)), 'Entertainment'),
            webobjs.DataTile('$' + str(round(other_agg, 2)), 'House'),
        ]

        return render_template('banker/insights.html', week_start=week_start, tiles=tiles)

    else:
        today = date.today()
        last_week_start = (today - timedelta(days=today.weekday() + 8))
        last_week_end = (today - timedelta(days=today.weekday() + 2))

        # get all database transaction data and filter for last month
        postgres_df = pd.read_sql_query(sql=text("SELECT * FROM citi_transaction_data"), con=engine.connect())
        postgres_df = postgres_df[(postgres_df['date'] >= last_week_start) & (postgres_df['date'] <= last_week_end)]

        # get aggregate value, if empty return 0
        gas_agg = get_category_agg('gas', postgres_df)
        grocery_agg = get_category_agg('grocery', postgres_df)
        entertainment_agg = get_category_agg('entertainment', postgres_df)
        other_agg = get_category_agg('house', postgres_df)

        tiles = [
            webobjs.DataTile('$' + str(round(gas_agg, 2)), 'Gas'),
            webobjs.DataTile('$' + str(round(grocery_agg, 2)), 'Grocery'),
            webobjs.DataTile('$' + str(round(entertainment_agg, 2)), 'Entertainment'),
            webobjs.DataTile('$' + str(round(other_agg, 2)), 'House'),
        ]

        return render_template('banker/insights.html', week_start=last_week_start, tiles=tiles)

    
def get_category_agg(category, _data, negative=False):
    category = [category] if type(category) is not list else category
    if not negative:
        cat_df = _data[_data['category'].isin(category)]
    else:
        cat_df = _data[~_data['category'].isin(category)]
        
    cat_agg_df = cat_df.groupby('category').agg({'debit': 'sum'})

    return cat_agg_df.values.tolist()[0][0] if not cat_agg_df.empty else 0