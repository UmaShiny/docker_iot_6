#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
from flask import jsonify
import requests
# my_script.py
import datetime
import os
import mysql.connector

def get_airoco_data_is_daemon():
    
    """
    index = {
    'Ｒ３ー４０１':'R3-401',
    'Ｒ３ー４０３':'R3-403',
    'Ｒ３ー３０１':'R3-301',
    'Ｒ３ー４Ｆ_ＥＨ':'R3-4F_EH',
    'Ｒ３ー３Ｆ_ＥＨ':'R3-3F_EH',
    'Ｒ３ー１Ｆ_ＥＨ':'R3-1F_WH',
    'Ｒ３ーB１Ｆ_ＥＨ':'R3-B1F_EH',
    }
    """

    res = requests.get('https://proxy.cep-hd-dlp.chuden.co.jp/data-n8suh89sqhcjo5g5/data-api/latest?id=CgETViZ2&subscription-key=0e35a874f02a4887adc1ed0b2561f645') # 実験室用

    Airoco_data = []
    for i in range(7):
        res_json = res.json()[i]
        sensorNumber = res_json['sensorNumber']
        # sensorName = res_json['sensorName'] => encoding error occurs
        if(res_json['sensorName'] != 'Ｒ３ー４０１') : continue
        # if sensorName not in index: continue # 未知のセンサーは無視
        # sensorName = index[res_json['sensorName']]
        co2 = res_json['co2']
        if co2==None: continue # データ無ければ次
        temperature = res_json['temperature']
        relativeHumidity = res_json['relativeHumidity']
        timestamp = res_json['timestamp']
        dt = datetime.datetime.fromtimestamp(timestamp)
        Airoco_data = [{
            'co2':co2,
            'temperature':temperature,
            'relativeHumidity':relativeHumidity,
        }]
    return Airoco_data

def main():
    
    print(f"Cron job executed at {datetime.datetime.now()}")
    db_config = {
        'user': 'root',
        'password': 'rootpassword',
        'host': 'db',
        'database': 'mydatabase'
    }
    print(db_config)
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    for data in get_airoco_data_is_daemon():
        cursor.execute("INSERT INTO sensor_table_R3_401 (co2, humidity, temperature) VALUES (%s, %s, %s)", (data['co2'], data['relativeHumidity'], data['temperature']))
        cnx.commit()
    cursor.close()
    cnx.close()

    print("db_test is done.\n")
    #print(get_airoco_data_is_daemon())

if __name__ == "__main__":
    main()
