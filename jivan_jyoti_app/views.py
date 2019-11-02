from django.http import HttpResponse
# from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
import pandas as pd
import json

from jivan_jyoti import config
from jivan_jyoti_app.utils import validate_pin, mobile_valid


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
        print("1111111111")
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
            'submit_date': new_dict['submit_date'][0], 'modify_date': new_dict['modify_date'][0],
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
    try:
        if request.method == 'POST':
            data = request.POST
            new_dict = dict(data)
            print(new_dict['mobile'][0])
            valid_mobile = config.mobile
            print(valid_mobile)
            if new_dict['mobile'][0] == valid_mobile:
                return HttpResponse(json.dumps({'msg': 'success', 'status': True, 'data': new_dict['mobile'][0]}))
            else:
                return HttpResponse(json.dumps({'msg': 'incorrect mobile number', 'status': False}))
    except Exception as e:
        return HttpResponse(json.dumps({'status': False, 'msg': str(e)}))


def volunteer_registration(request):
    """

    :param request:
    :return:
    """
    try:
        if request.method == 'POST':
            data = request.POST

    except Exception as e:
        return HttpResponse(json.dumps({'status': False, 'msg': str(e)}))

