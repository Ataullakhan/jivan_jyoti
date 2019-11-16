from uuid import uuid1
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from datetime import date
import datetime
import pandas as pd
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
        today = date.today()
        submit_date = today.strftime("%Y/%m/%d")
        modified_date =today.strftime("%Y/%m/%d")
        data = request.POST
        new_dict = dict(data)
        pincode = new_dict['pin_code'][0]
        mobile = new_dict['mobile'][0]
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
            'state': new_dict['state'][0], 'district': new_dict['district'][0]
        }
        insert_query = "insert into ragistration_form(submit_date, modify_date, " \
                       "name, father_husband_name, mother_name, " \
                       "gender, DOB, marital_status, education, education_status, " \
                       "occupation, occupation_description, mobile, flat_room_block_no," \
                       " premises_building_villa, road_street_lane, " \
                       "area_locality_taluk, pin_code, state, district)" \
                       + " VALUES('{submit_date}', '{modify_date}', " \
                         "'{name}', '{father_husband_name}', '{mother_name}', '{gender}', " \
                         "'{DOB}', '{marital_status}', '{education}', '{education_status}', " \
                         "'{occupation}', '{occupation_description}', '{mobile}', " \
                         "'{flat_room_block_no}', '{premises_building_villa}', '{road_street_lane}', " \
                         "'{area_locality_taluk}', '{pin_code}', '{state}', '{district}')".format(**params)

        cursor = connection.cursor()
        cursor.execute(insert_query)
        url = "http://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/ADDON_SERVICES/SEND/TSMS"
        payload = "{\"From\": \"JIVANJ\",\"To\": \""+mobile+"'\", \"Msg\": \"Hi "+new_dict['name'][0]+", Your JIVAN JYOTI registration successful.\"}"
        response = requests.request("POST", url, data=payload)
        return HttpResponse(json.dumps({'Message': 'Success', 'status': True, 'data': response.text}))
    # except Exception as e:
    #     return HttpResponse(json.dumps({'status': False, 'msg': str(e)}))


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
            send_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/+91"+valid_mobile+"/AUTOGEN"
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
            recive_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/VERIFY/" + session_id + "/" +otp
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
        print('otppp',otp)
        if otp == '' or otp == None:
            truncate_query = "truncate session_id_table;"
            cursor = connection.cursor()
            cursor.execute(truncate_query)

            print("in volunteer user input section")
            image = request.FILES['image']
            # if request.session['image'] != None:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            image_url = path + '/' + filename
            print('image_url', image_url)

            uuid = uuid1()
            print('uuid', uuid)
            params = {
                'image': image_url,
                'gender': request.POST.get('gender'),
                'mobile': request.POST.get('mobile'),
                'address': request.POST.get('address'),
                'status': 'Panding',
                'id': uuid,
                'name': request.POST.get('name')
            }
            print(params)
            insert_query = "insert into volunteer_registration(image_url, gender, mobile, address, status, id, name)" \
                           + " VALUES('{image}', '{gender}', '{mobile}', '{address}', '{status}', '{id}', '{name}')".format(**params)

            print('insert_query', insert_query)
            cursor = connection.cursor()
            cursor.execute(insert_query)

            admin_number = config.mobile
        # if mobile_valid(request.session['mobile']):
            send_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/+91" + admin_number + "/AUTOGEN"
            response = requests.request("POST", send_otp_url)
            request.session['response_text'] = response.text
            print('response texttt', response.text)

            res = ast.literal_eval(response.text)
            session_id = res['Details']
            params = {
                'session_id': session_id,
                'id': uuid
            }

            insert_query = "insert into session_id_table(session_id, id) VALUES('{session_id}', '{id}')".format(**params)
            cursor = connection.cursor()
            cursor.execute(insert_query)
            return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': response.text}))

        elif otp != '' or otp != None:
            print("in voluenteer otp section")
            query = "select session_id, id from session_id_table;"
            df = getdata(query)
            session_id = df['session_id'][0]
            id = df['id'][0]
            print('session_id', session_id)
            print('id', id)
            print('000000000', otp)
            recive_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/VERIFY/" + session_id + "/" +otp
            response = requests.request("POST", recive_otp_url)
            request.session['response_text1'] = response.text
            otp_val = request.session['response_text1']
            res1 = ast.literal_eval(otp_val)
            status = res1['Details']
            print(status)

            if status == 'OTP Matched':
                update_query = "UPDATE volunteer_registration " \
                               "SET status = 'Matched' where id = '{id}'".format(**{'id': id})

                print(update_query)
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
        get_data_query = "select * from ragistration_form"
        df = getdata(get_data_query)
        df['submit_date'] = df['submit_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'))
        df['modify_date'] = df['modify_date'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'))
        df['dob'] = df['dob'].apply(lambda x: datetime.datetime.strftime(x, '%Y-%m-%d'))

        data = df.to_dict('records')
        return HttpResponse(json.dumps({'data': data}))



@csrf_exempt
def fatch_volunteer_data(request):
    """

    :param request:
    :return:
    """
    if request.method == 'POST':
        get_data_query = "select name, image_url, gender, mobile, address from volunteer_registration;"
        df = getdata(get_data_query)

        data = df.to_dict('records')
        return HttpResponse(json.dumps({'data': data}))



