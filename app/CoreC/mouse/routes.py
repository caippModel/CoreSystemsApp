from io import BytesIO

import mysql.connector as connection
import pandas as pd
import pymysql
from app import login_required
from app.CoreC.mouse import bp
from app.CoreC.mouse.mouseTable import mouseTable
from app.utils.db_utils import db_utils
from app.utils.logging_utils.logGenerator import Logger
from flask import (Flask, flash, jsonify, make_response, redirect,
                   render_template, request, send_file, url_for)
from flask_caching import Cache
from flask_paginate import Pagination, get_page_args
from flask_login import current_user

# mouse object
mouseTable = mouseTable()

# Cache setup
app = Flask(__name__)
cache1 = Cache(app, config={'CACHE_TYPE': 'simple'}) # Memory-based cache
defaultCache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Logging set up
logFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LogGenerator = Logger(logFormat=logFormat, logFile='application.log')
logger = LogGenerator.generateLogger()

@bp.route('/mouse', methods=['GET', 'POST'])
@login_required(role=["user", "coreC"])
def mouse():
    if request.method == 'POST':
        rawInputs = request.form

        inputDict = rawInputs.to_dict()
        print(inputDict)
        Uinputs = list(inputDict.values())

        sort = inputDict["sort"]

        Uinputs.pop(-1)

        data: dict = mouseTable.display(Uinputs, sort)

        with app.app_context():
            cache1.delete('cached_dataframe') # Clear the cache when new filters are applied
            cache1.set('cached_dataframe', data, timeout=3600)  # Cache for 1 hour (3600 seconds)
    
    if request.method == 'GET':
        with app.app_context():
            cached_data = cache1.get('cached_dataframe')
        
        if cached_data is None:
            with app.app_context():
                defaultCache.delete('cached_dataframe')

            df = db_utils.toDataframe("SELECT * FROM Mouse_Stock WHERE Genotype != 'N/A';", 'app/Credentials/CoreC.json')
            df.rename(columns={'PI_Name': 'PI', 'Mouse_Description': 'Description', 'Times_Back_Crossed': 'Times Back Crossed', 'MTA_Required': 'MTA Required'}, inplace=True)
        
            data = df.to_dict('records')

            with app.app_context():
                defaultCache.set('cached_dataframe', data, timeout=3600)
        else:
            # Try to get the cached DataFrame
            with app.app_context():
                data = cache1.get('cached_dataframe')

    page, per_page, offset = get_page_args(page_parameter='page', 
                                        per_page_parameter='per_page')

    if not current_user.is_admin:
        per_page = request.args.get('per_page', 20, type=int)
        offset = (page - 1) * per_page
    
    #number of rows in table
    num_rows = len(data)

    pagination_users = data[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=num_rows)
    
    # use to prevent user from caching pages
    response = make_response(render_template("CoreC/mouse_stock.html", data=pagination_users, page=page, per_page=per_page, pagination=pagination, list=list, len=len, str=str, num_rows=num_rows))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    return response
    
@bp.route('/addMouse', methods=['GET', 'POST'])
@login_required(role=["user", "coreC"])
def addMouse():
    if request.method == 'POST':
        inputs = request.form
        
        inputData = inputs.to_dict()

        has_empty_value = any(value == "" or value is None for value in inputData.values())
        
        if has_empty_value:
            flash('Fields cannot be empty')
            return redirect(url_for('mouse.addMouse'))
        
        if not inputData["Times Back Crossed"].isdigit():
            flash('"Times Back Crossed" must be a number')
            return redirect(url_for('mouse.addMouse'))

        df = mouseTable.add(inputData)
        df.rename(columns={'PI_Name': 'PI', 'Mouse_Description': 'Description', 'Times_Back_Crossed': 'Times Back Crossed', 'MTA_Required': 'MTA Required'}, inplace=True)
        data = df.to_dict(orient='records')
        
        page, per_page, offset = get_page_args(page_parameter='page', 
                                           per_page_parameter='per_page')
        
        #number of rows in table
        num_rows = len(data)

        pagination_users = data[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=num_rows)
        
        # use to prevent user from caching pages
        response = make_response(render_template("CoreC/mouse_stock.html", data=pagination_users, page=page, per_page=per_page, pagination=pagination, list=list, len=len, str=str, num_rows=num_rows))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
        response.headers["Pragma"] = "no-cache" # HTTP 1.0.
        response.headers["Expires"] = "0" # Proxies.
        return response
    
    if request.method == 'GET':
        data = {
            "PI": "",
            "Genotype": "",
            "Description": "",
            "Strain": "",
            "Times Back Crossed": "",
            "MTA Required": "",
        }

        # use to prevent user from caching pages
        response = make_response(render_template('CoreC/add_mouse.html', fields = data))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
        response.headers["Pragma"] = "no-cache" # HTTP 1.0.
        response.headers["Expires"] = "0" # Proxies.
        return response
    
@bp.route('/changeMouse', methods=['GET', 'POST'])
@login_required(role=["user", "coreC"])
def changeMouse():
    if request.method == 'POST':
        inputs = request.form
            
        inputData = inputs.to_dict()

        has_empty_value = any(value == "" or value is None for value in inputData.values())
        
        if has_empty_value:
            flash('Fields cannot be empty')
            return redirect(url_for('mouse.addMouse'))
        
        if not inputData["Times Back Crossed"].isdigit():
            flash('"Times Back Crossed" must be a number')
            return redirect(url_for('mouse.addMouse'))
        print(f"Input Data: {inputData}")
        #Executes change query
        mouseTable.change(inputData)

        # use to prevent user from caching pages
        response = make_response(redirect(url_for('mouse.mouse')))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
        response.headers["Pragma"] = "no-cache" # HTTP 1.0.
        response.headers["Expires"] = "0" # Proxies.
        return response
    
    if request.method == 'GET':
        primary_key = request.args.get('primaryKey')
        query = "SELECT * FROM Mouse_Stock WHERE Stock_ID = %s;"
        df = db_utils.toDataframe(query, 'app/Credentials/CoreC.json', params=(primary_key,))
        df.rename(columns={'PI_Name': 'PI', 'Mouse_Description': 'Description', 'Times_Back_Crossed': 'Times Back Crossed', 'MTA_Required': 'MTA Required'}, inplace=True)

        data = df.to_dict()
        
        # use to prevent user from caching pages
        response = make_response(render_template('CoreC/change_mouse.html', fields = data, pkey = primary_key))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
        response.headers["Pragma"] = "no-cache" # HTTP 1.0.
        response.headers["Expires"] = "0" # Proxies.
        return response
    
@bp.route('/deleteMouse', methods=['POST'])
@login_required(role=["user", "coreC"])
def deleteMouse():
    primary_key = request.form['primaryKey']

    logger.info("Deletion Attempting...")

    mouseTable.delete(primary_key)

    # use to prevent user from caching pages
    response = make_response(redirect(url_for('mouse.mouse')))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate" # HTTP 1.1.
    response.headers["Pragma"] = "no-cache" # HTTP 1.0.
    response.headers["Expires"] = "0" # Proxies.
    return response

@bp.route('/downloadMouseCSV', methods=['GET'])
@login_required(role=["user", "coreC"])
def downloadCSV():
    with app.app_context():
        saved_data = cache1.get('cached_dataframe')
    
    if saved_data is None:
        with app.app_context():
            saved_data = defaultCache.get('cached_dataframe')

    csv_io = mouseTable.download_CSV(saved_data=saved_data, dropCol=['Stock_ID', 'user_id'])
    
    return send_file(csv_io, mimetype='text/csv', as_attachment=True, download_name='Mouse Data.csv')