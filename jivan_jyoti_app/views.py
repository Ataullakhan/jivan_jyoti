from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
# from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from datetime import date
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
        print('data', data)
        new_dict = dict(data)
        print("new_dict", new_dict)
        pincode = new_dict['pin_code'][0]
        print("pincode", pincode)
        mobile = new_dict['mobile'][0]
        print('mobile', mobile)
        if validate_pin(pincode) is True:
            print('22222222222')
            pincode = pincode
        else:
            print('333333333')
            return HttpResponse(json.dumps({"Message": 'Pincode is not correct', 'status': False}))
        if mobile_valid(mobile):
            print('4444444')
            mobile = mobile
        else:
            print('555555555')
            return HttpResponse(json.dumps({"Message": 'mobile number is not correct', 'status': False}))
        params = {
            'submit_date': submit_date, 'modify_date': modified_date,
            'family_unique_id': new_dict['family_unique_id'][0],
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
        print('params', params)
        insert_query = "insert into ragistration_form(submit_date, modify_date, " \
                       "family_unique_id, name, father_husband_name, mother_name, " \
                       "gender, DOB, marital_status, education, education_status, " \
                       "occupation, occupation_description, mobile, flat_room_block_no," \
                       " premises_building_villa, road_street_lane, " \
                       "area_locality_taluk, pin_code, state, district)" \
                       + " VALUES('{submit_date}', '{modify_date}', '{family_unique_id}', " \
                         "'{name}', '{father_husband_name}', '{mother_name}', '{gender}', " \
                         "'{DOB}', '{marital_status}', '{education}', '{education_status}', " \
                         "'{occupation}', '{occupation_description}', '{mobile}', " \
                         "'{flat_room_block_no}', '{premises_building_villa}', '{road_street_lane}', " \
                         "'{area_locality_taluk}', '{pin_code}', '{state}', '{district}')".format(**params)

        print('insert_query', insert_query)
        cursor = connection.cursor()
        cursor.execute(insert_query)
        print("555555555")
        
        return HttpResponse(json.dumps({'Message': 'Success', 'status': True, 'data': 'Saved into database'}))
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
            send_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/+91"+valid_mobile+"/AUTOGEN"
            response = requests.request("POST", send_otp_url)
            request.session['responce_text'] = response.text
            return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': response.text}))

        elif otp != '' and otp != None:
            res = request.session['responce_text']
            res = ast.literal_eval(res)
            session_id = res['Details']
            recive_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/VERIFY/" + session_id + "/" +otp
            response = requests.request("POST", recive_otp_url)
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
        print('otppp', otp)
        if otp == '' or otp == None:
            image = request.FILES['image']
            # if request.session['image'] != None:
            fs = FileSystemStorage()
            filename = fs.save(image.name, image)
            image_url = path + '/' + filename
            print('image_url', image_url)
            request.session['image_url'] = image_url
            request.session['gender'] = request.POST.get('gender')
            request.session['mobile'] = request.POST.get('mobile')
            request.session['address'] = request.POST.get('address')

            admin_number = config.mobile
            print(request.session['mobile'])
        # if mobile_valid(request.session['mobile']):
            send_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/+91" + admin_number + "/AUTOGEN"
            response = requests.request("POST", send_otp_url)
            request.session['responce_text'] = response.text
            print('response texttt', response.text)
            return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': response.text}))

        elif otp != '' or otp != None:
            res = request.session['responce_text']
            res = ast.literal_eval(res)
            session_id = res['Details']
            recive_otp_url = "https://2factor.in/API/V1/7fe951b0-fb11-11e9-9fa5-0200cd936042/SMS/VERIFY/" + session_id + "/" + otp
            response = requests.request("POST", recive_otp_url)
            request.session['responce_text1'] = response.text
            otp_val = request.session['responce_text1']
            res1 = ast.literal_eval(otp_val)
            status = res1['Details']
            print(status)

            if status == 'OTP Matched':
                params = {
                    'image': request.session['image_url'],
                    'gender': request.session['gender'],
                    'mobile': request.session['mobile'],
                    'address': request.session['address']
                }
                print(params)
                insert_query = "insert into volunteer_registration(image_url, gender, mobile, address)" \
                               + " VALUES('{image}', '{gender}', '{mobile}', '{address}')".format(**params)

                print('insert_query', insert_query)
                cursor = connection.cursor()
                cursor.execute(insert_query)

            return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': response.text}))




    # except Exception as e:
    #     return HttpResponse(json.dumps({'status': False, 'msg': str(e)}))

