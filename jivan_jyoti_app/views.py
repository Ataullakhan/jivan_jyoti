from uuid import uuid1

import psycopg2
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from datetime import date
import datetime
import pandas as pd
import strgen
import json
import requests
import ast

from jivan_jyoti import config, settings
from jivan_jyoti_app.utils import validate_pin, mobile_valid

path = settings.MEDIA_ROOT


def getlowerdf(df):
    """
    function for fetch and manage columns
    :param df:
    :return:
    """
    cols = df.columns
    cols_dict = {}
    for item in cols:
        cols_dict[item] = item.lower()
    df.rename(columns=cols_dict, inplace=True)
    return df


def getdata(qry, todict=False, single=False):
    """
    function for fetch querys and stabilised connection with datatables
    :param qry:
    :param todict:
    :param single:
    :return:
    """
    data = pd.read_sql(qry, connection)
    # connection.close()
    data = getlowerdf(data)
    data = data.fillna(0)
    if todict:
        data = data.to_dict(orient="records")
        if single:
            data = data[0]
    return data


@csrf_exempt
def registration_form(request):
    """
    # get data from registration form and saved into database
    :return: form values
    """
    # try:
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == '' or otp == None:
            today = date.today()
            submit_date = today.strftime("%Y/%m/%d")
            modified_date = today.strftime("%Y/%m/%d")
            data = request.POST
            uuid = uuid1()
            new_dict = dict(data)
            pincode = new_dict['pin_code'][0]
            mobile = new_dict['mobile'][0]
            unique_id = new_dict['unique_id'][0]

            if unique_id == '' or unique_id is None:
                unique_id = strgen.StringGenerator("JJ-[\d][A-Z]{6}").render()
                head_number = new_dict['mobile'][0]
            else:
                head_number_query = "select mobile from ragistration_form where unique_id = '{0}'".format(unique_id)
                df = getdata(head_number_query)
                head_number = df['mobile'].iloc[0]

            if validate_pin(pincode) is True:
                pincode = pincode
            else:
                return HttpResponse(json.dumps({"Message": 'Pincode is not correct', 'status': False}))
            if mobile_valid(mobile):
                mobile = mobile
            else:
                return HttpResponse(json.dumps({"Message": 'mobile number is not correct', 'status': False}))
            params = {
                'submit_date': submit_date, 'modify_date': modified_date,
                'name': new_dict['name'][0], 'father_husband_name': new_dict['father_husband_name'][0],
                'mother_name': new_dict['mother_name'][0], 'gender': new_dict['gender'][0],
                'DOB': new_dict['DOB'][0], 'marital_status': new_dict['marital_status'][0],
                'education': new_dict['education'][0], 'education_status': new_dict['education_status'][0],
                'occupation': new_dict['occupation'][0],
                'occupation_description': new_dict['occupation_description'][0],
                'mobile': mobile, 'flat_room_block_no': new_dict['flat_room_block_no'][0],
                'premises_building_villa': new_dict['premises_building_villa'][0],
                'road_street_lane': new_dict['road_street_lane'][0],
                'area_locality_taluk': new_dict['area_locality_taluk'][0], 'pin_code': pincode,
                'state': new_dict['state'][0], 'district': new_dict['district'][0],
                'education_description': new_dict['education_description'][0],
                'unique_id': unique_id, 'status': 'Panding', 'id': uuid
            }
            insert_query = "insert into ragistration_form(submit_date, modify_date, " \
                           "name, father_husband_name, mother_name, " \
                           "gender, DOB, marital_status, education, education_status, " \
                           "occupation, occupation_description, mobile, flat_room_block_no," \
                           " premises_building_villa, road_street_lane, " \
                           "area_locality_taluk, pin_code, state, district, education_description," \
                           " unique_id, status, id)" \
                           + " VALUES('{submit_date}', '{modify_date}', " \
                             "'{name}', '{father_husband_name}', '{mother_name}', '{gender}', " \
                             "'{DOB}', '{marital_status}', '{education}', '{education_status}', " \
                             "'{occupation}', '{occupation_description}', '{mobile}', " \
                             "'{flat_room_block_no}', '{premises_building_villa}', '{road_street_lane}', " \
                             "'{area_locality_taluk}', '{pin_code}', '{state}', " \
                             "'{district}', '{education_description}'," \
                             " '{unique_id}', '{status}', '{id}')".format(**params)

            cursor = connection.cursor()
            cursor.execute(insert_query)
            url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS" \
                  "/+91" + head_number + "/AUTOGEN/JivanJyotiadminotp"

            response = requests.request("POST", url)

            res = ast.literal_eval(response.text)
            session_id = res['Details']
            params = {
                'session_id': session_id,
                'id': uuid
            }

            insert_query = "insert into session_id_table(session_id, id) VALUES('{session_id}', '{id}')".format(
                **params)
            cursor = connection.cursor()
            cursor.execute(insert_query)
            url = "http://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/ADDON_SERVICES/SEND/TSMS"
            payload = "{\"From\": \"JIVANJ\",\"To\": \"" + head_number + "'\", \"Msg\": \"Hi " + new_dict['name'][
                0] + " Applied For User Registration with this Unique ID: " + unique_id + "\"}"
            response = requests.request("POST", url, data=payload)
            return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': response.text}))

        elif otp != '' or otp is not None:
            query = "select session_id, id from session_id_table;"
            df = getdata(query)
            session_id = df['session_id'][0]
            id = df['id'][0]
            recive_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/VERIFY/" + session_id + "/" + otp
            response = requests.request("POST", recive_otp_url)
            otp_val = response.text
            res1 = ast.literal_eval(otp_val)
            status = res1['Details']

            if status == 'OTP Matched':
                update_query = "UPDATE ragistration_form " \
                               "SET status = 'Matched' where id = '{id}'".format(**{'id': id})

                cursor = connection.cursor()
                cursor.execute(update_query)

                truncate_query = "truncate session_id_table;"
                cursor = connection.cursor()
                cursor.execute(truncate_query)

            return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': response.text}))


@csrf_exempt
def admin_registration(request):
    """

    :param request:
    :return:
    """
    # try:
    if request.method == 'POST':
        otp = request.POST.get('otp')
        mobile = request.POST.get('mobile')
        valid_mobile = config.mobile
        if mobile == valid_mobile:
            print("in admin number section")
            send_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/+91" + valid_mobile + "/AUTOGEN/JivanJyotiadminotp"
            response = requests.request("POST", send_otp_url)
            print('------------', response.text)
            res = ast.literal_eval(response.text)
            session_id = res['Details']
            params = {
                'session_id': session_id
            }
            insert_query = "insert into session_id_table(session_id) VALUES('{session_id}')".format(**params)
            cursor = connection.cursor()
            cursor.execute(insert_query)
            return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': response.text}))

        elif otp != '' and otp != None:
            print("in admin otp section")
            query = "select session_id from session_id_table;"
            df = getdata(query)
            session_id = df['session_id'][0]
            print(session_id)
            recive_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/VERIFY/" + session_id + "/" + otp
            response = requests.request("POST", recive_otp_url)
            truncate_query = "truncate session_id_table;"
            cursor = connection.cursor()
            cursor.execute(truncate_query)
            return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': response.text}))
        else:
            return HttpResponse(json.dumps({'msg': 'incorrect mobile number', 'status': False}))

    # except Exception as e:
    #     return HttpResponse(json.dumps({'status': False, 'msg': str(e)}))


@csrf_exempt
def volunteer_registration(request):
    """

    :param request:
    :return:
    """
    # try:
    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == '' or otp == None:
            truncate_query = "truncate session_id_table;"
            cursor = connection.cursor()
            cursor.execute(truncate_query)
            image = request.FILES['image']
            # if request.session['image'] != None:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            image_url = 'http://35.224.167.35/media/' + filename
            uuid = uuid1()
            params = {
                'image': image_url,
                'gender': request.POST.get('gender'),
                'mobile': request.POST.get('mobile'),
                'status': 'Panding',
                'id': uuid,
                'name': request.POST.get('name'),
                'fathername': request.POST.get('fathername'),
                'dateofbirth': request.POST.get('dateofbirth'),
                'flat_room_block_no': request.POST.get('flat_room_block_no'),
                'premises_building_villa': request.POST.get('premises_building_villa'),
                'road_street_lane': request.POST.get('road_street_lane'),
                'area_locality_taluk': request.POST.get('area_locality_taluk'),
                'pin_code': request.POST.get('pin_code'),
                'state': request.POST.get('state'),
                'district': request.POST.get('district'),
            }
            print(params)
            insert_query = "insert into volunteer_registration" \
                           "(image_url, gender, mobile, status, id, name, fathername, dateofbirth, " \
                           "flat_room_block_no, premises_building_villa, road_street_lane, area_locality_taluk," \
                           "pin_code, state, district)" \
                           + " VALUES('{image}', '{gender}', '{mobile}', '{status}', '{id}'," \
                             " '{name}', '{fathername}', '{dateofbirth}'," \
                             " '{flat_room_block_no}', '{premises_building_villa}'," \
                             " '{road_street_lane}', '{area_locality_taluk}', '{pin_code}', '{state}'," \
                             " '{district}')".format(**params)

            print('insert_query', insert_query)
            cursor = connection.cursor()
            try:
                cursor.execute(insert_query)
            except (Exception, psycopg2.Error) as error:
                return HttpResponse(json.dumps({'status': False, 'data': str(error)}))

            admin_number = config.mobile

            # if mobile_valid(request.session['mobile']):
            url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/+91" + admin_number + "/AUTOGEN/JivanJyotiadminotp"

            payload = "{\"From\": \"JIVANJ\", \"To\": \"" + admin_number + "'\", \"Msg\": \"Volunteer Mobile Number: " + request.POST.get(
                'mobile') + ", for JIVAN JYOTI registration.\"}"
            headers = {'content-type': "application/x-www-form-urlencoded"}
            response = requests.request("POST", url, data=payload, headers=headers)

            res = ast.literal_eval(response.text)
            session_id = res['Details']
            params = {
                'session_id': session_id,
                'id': uuid
            }

            insert_query = "insert into session_id_table(session_id, id) VALUES('{session_id}', '{id}')".format(
                **params)
            cursor = connection.cursor()
            cursor.execute(insert_query)
            return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': response.text}))

        elif otp != '' or otp != None:
            query = "select session_id, id from session_id_table;"
            df = getdata(query)
            session_id = df['session_id'][0]
            id = df['id'][0]
            recive_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/VERIFY/" + session_id + "/" + otp
            response = requests.request("POST", recive_otp_url)
            request.session['response_text1'] = response.text
            otp_val = request.session['response_text1']
            res1 = ast.literal_eval(otp_val)
            status = res1['Details']

            if status == 'OTP Matched':
                update_query = "UPDATE volunteer_registration " \
                               "SET status = 'Matched' where id = '{id}'".format(**{'id': id})

                cursor = connection.cursor()
                cursor.execute(update_query)

                truncate_query = "truncate session_id_table;"
                cursor = connection.cursor()
                cursor.execute(truncate_query)

            return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': response.text}))

    # except Exception as e:
    #     return HttpResponse(json.dumps({'status': False, 'msg': str(e)}))


@csrf_exempt
def fatch_ragistration_data(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        get_data_query = "select * from ragistration_form where status = 'Matched';"
        df = getdata(get_data_query)
        df['submit_date'] = df['submit_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'))
        df['modify_date'] = df['modify_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'))
        df['dob'] = df['dob'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'))

        excel_path = path + "/excel_file/output.xlsx"
        df.to_excel(excel_path, engine='xlsxwriter')

        print(excel_path)

        data = df.to_dict('records')
        return HttpResponse(json.dumps({'data': data}))


@csrf_exempt
def fatch_volunteer_data(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        get_data_query = "select * from volunteer_registration where status = 'Matched';"
        df = getdata(get_data_query)
        df['dateofbirth'] = df['dateofbirth'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'))

        data = df.to_dict('records')
        return HttpResponse(json.dumps({'data': data}))
