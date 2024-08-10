import datetime
import random

from flask import Flask,request
import  json
from db_connection import db_connection
from services import emailSending
app = Flask(__name__)

DB_ERR = json.dumps([{'text':"DB CONN FAILED",
                 'status':400}])
QUERY_ERR = json.dumps([{'text':"QUERY EXECUTION FAILED",'status':400}])

@app.route('/')
def home():
    query = "SELECT * FROM vehicle_details"
    conn = db_connection.Connection()
    if hasattr(conn,'no_connection'):
        return DB_ERR

    response = conn.custom_query(query=query)
    if response==1:
        return QUERY_ERR
    formated_data = []
    for data in response:
        vehicle_id,owner_id,license_plate_no,model = data
        formated_data.append({
            "vehicle_id":vehicle_id,
            "owner_id":owner_id,
            "license_plate_no":license_plate_no,
            "model":model
        })
    formated_data  = json.dumps(formated_data)
    return formated_data

# @app.route('/all_owner_details')
# def all_owner_details():
#     query = f"SELECT * FROM owner_details"
#     conn = db_connection.Connection()
#     if hasattr(conn,'no_connection'):
#         return DB_ERR
#
#     response = conn.custom_query(query=query)
#     if response==1:
#         return QUERY_ERR
#     formated_data = []
#
#     for data in response:
#         owner_id,name,email = data
#         formated_data.append({
#             "owner_id":owner_id,
#             "name":name,
#             "email":email
#         })
#     formated_data  = json.dumps(formated_data)
#     return formated_data

@app.route('/owner_details')
def owner_details():
    id = request.args.get('id',"")

    if id!="":
        query = f"SELECT * FROM owner_details where owner_id = '{str(id).upper()}'"
    else:
        query = f"SELECT * FROM owner_details"
    conn = db_connection.Connection()
    if hasattr(conn,'no_connection'):
        return DB_ERR

    response = conn.custom_query(query=query)
    if response==1:
        return QUERY_ERR
    formated_data = []
    for data in response:
        owner_id,name,email = data
        formated_data.append({
            "owner_id":owner_id,
            "name":name,
            "email":email
        })
    formated_data  = json.dumps(formated_data)
    return formated_data

@app.route('/add/owner_details')
def add_owner_details():

    name = request.args.get('name',"")
    email = request.args.get('email',"")
    OWNER_ID = request.args.get('owner_id',"")

    query = f"INSERT INTO OWNER_DETAILS VALUES ('{OWNER_ID}','{name}','{email}')"
    if name=="" or email=="" :
        err = json.dumps([{"Err":"Not fulfilled the required data",'status':400}])
        return err
    conn = db_connection.Connection()
    if hasattr(conn,'no_connection'):
        return DB_ERR
    response = conn.custom_query(query=query)
    if response==1:
        return QUERY_ERR
    return response

@app.route('/add/vehicle_details')
def add_vehicle_details():
    owner_name=request.args.get('owner_name',"")
    owner_email=request.args.get('owner_email',"")
    owner_id=request.args.get('owner_id',"")
    license_plate=request.args.get('license_plate_no',"")
    model=request.args.get('args',"")
    vehicle_id=request.args.get('vehicle_id',"")

    query = f"INSERT INTO VEHICLE_DETAILS VALUES('{vehicle_id}','{owner_id}','{license_plate}','{model}')"

    if owner_name=="" or owner_email=="" or owner_id=="" or license_plate=="" or model=="":
        err = json.dumps([{"Err": "Not fulfilled the required data", 'status': 400}])
        return err
    conn=db_connection.Connection()
    if hasattr(conn,'no_connection'):
        return DB_ERR
    response=conn.custom_query(query=query)
    if response==1:
        return QUERY_ERR
    with open('html_email/welcome.html','r') as file:
        body=file.read()
        body=body.replace("{{OWNER_ID}}",owner_id)
        body = body.replace('{{OWNER_NAME}}',owner_name)
        body=body.replace('{{VEHICLE_ID}}',vehicle_id)
        body=body.replace('{{VEHICLE_MODEL}}',model)
        body=body.replace('{{LICENSE_PLATE_NUMBER}}',license_plate)
    emailSending.send_email(receiver_email=[owner_email],subject=f'Registration Successful for {owner_id}',body=body,body_type='html')
    return response

@app.route('/update/owner_details')
def update_owner_details():
    old_name = request.args.get('old_name',"")
    old_email = request.args.get('new_email',"")
    new_name = request.args.get('new_name',"")
    new_email=request.args.get('new_email',"")
    owner_id = request.args.get('owner_id',"")

    query = f"UPDATE OWNER_DETAILS set name ='{new_name}',email='{new_email}' where owner_id ='{owner_id}'"

    if old_name=="" or old_email=="" or new_name=="" or new_email=="" or owner_id == "":
        err = json.dumps([{"Err": "Not fulfilled the required data", 'status': 400}])
        return err
    conn = db_connection.Connection()
    if hasattr(conn,'no_connection'):
        return DB_ERR
    response = conn.custom_query(query=query)
    if response==1:
        return QUERY_ERR
    with open('html_email/update_owner_details.html', 'r') as file:
        # read the html file and replace all the required changes
        body = file.read()
        body = body.replace('{old_name}', old_name)
        body = body.replace('{old_email}', old_email)
        body = body.replace('{new_name}', new_name)
        body = body.replace('{new_email}', new_email)
    emailSending.send_email(receiver_email=[old_email,new_email],subject="UPDATE SUCCESSFUL",body=body,body_type='html')
    return response


if __name__ == '__main__':
    app.run(debug=True)