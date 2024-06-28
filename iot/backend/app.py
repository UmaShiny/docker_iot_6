from flask import Flask, jsonify, request, send_file
import mysql.connector
import os
import requests
import numpy as np
import base64

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify(message="Hello from Flask!")


@app.route('/db')
def db_test():
    db_config = {
        'user': os.getenv('DATABASE_USER'),
        'password': os.getenv('DATABASE_PASSWORD'),
        'host': os.getenv('DATABASE_HOST'),
        'database': os.getenv('DATABASE_NAME')
    }
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    cursor.close()
    cnx.close()
    return jsonify(tables=tables)


@app.route('/getinfo')
def db_get_data():
    db_config = {
        'user': os.getenv('DATABASE_USER'),
        'password': os.getenv('DATABASE_PASSWORD'),
        'host': os.getenv('DATABASE_HOST'),
        'database': os.getenv('DATABASE_NAME')   
    }
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users;")
    tables = cursor.fetchall()
    cursor.close()
    cnx.close()
    return jsonify(tables=tables)


@app.route('/compare_info', methods=['GET'])
def user_certification():
    try:
        # リクエストされたときのurlを取得する
        url = request.url
        param_username = request.args.get('username')
        param_password = request.args.get('password')

        db_config = {
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
            'database': os.getenv('DATABASE_NAME')   
        }
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute(" SELECT id FROM users where username = %s AND password = %s;", (param_username, param_password))
        tables = cursor.fetchall()
        cursor.close()
        cnx.close()

        if param_username is None or param_password is None:
            return jsonify(message="username and password are required : {}".format(url)), 400
        else:
            return jsonify({
                'param_username': param_username,
                'db_id': tables[0][0],
                'param_password': param_password,
            })
    except:
        return jsonify(message="An error occurred"), 500


@app.route('/checkMailFromNodeRED', methods=['GET'])
def checkMailFromNodeRED():
    param_mail_user = ""
    param_mail_domain = ""

    try:
        # リクエストされたときのurlを取得する
        url = request.url
        #param_mail = request.args.get('email')
        param_mail_user = request.args.get('user')
        param_mail_domain = request.args.get('domain')

        param_mail = param_mail_user + "@" + param_mail_domain

        if param_mail is None:
            return jsonify(message="email are required : {}".format(url)), 400

        db_config = {
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
            'database': os.getenv('DATABASE_NAME')   
        }

        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("SELECT email FROM users where email = %s;", (param_mail,))
        tables = cursor.fetchall()
        cursor.close()
        cnx.close()

        if param_mail == [0][0]:
            return jsonify({
                'message': 'this mail is already registered',
                'mail': param_mail,
                'url': url
            })
        if tables == []:
            return jsonify({
                'message': 'this is not registered mail',
                'mail': param_mail,
                'url': url,
                'state': 'already'
            })
        else:
            return jsonify(message="An mail-check-error occurred"), 500
    except:
        return jsonify({
            'message': 'An error occurred',
            'mail': param_mail,
            'url': url,
            'tables': tables
        }), 500


@app.route('/resister_otk', methods=['GET'])
def user_certification_otk():
    
    param_mail_user = ""
    param_mail_domain = ""

    try:
        # リクエストされたときのurlを取得する
        url = request.url
        param_mail_user = request.args.get('user')
        param_mail_domain = request.args.get('domain')
        param_one_time_key = request.args.get('one_time_key')
        
        param_email = param_mail_user + "@" + param_mail_domain

        #if param_email is None or param_one_time_key is None:
        #return jsonify(message="username and password are required : {}".format(url)), 400


        db_config = {
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
            'database': os.getenv('DATABASE_NAME')   
        }
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO one_time_keys (email, one_time_key, expiration_time) VALUES(%s, %s, DATE_ADD(NOW(), INTERVAL 10 MINUTE));", (param_email, param_one_time_key))
        cnx.commit()

        # return jsonify(message="username and password are required : {}".format(url)), 400

        cursor.execute("SELECT * FROM one_time_keys where email = %s AND one_time_key = %s;", (param_email, param_one_time_key))
        tables = cursor.fetchall()
        cursor.close()
        cnx.close()

        
        return jsonify({
            'param_email': param_email,
            'expiration_time': tables[0][3],
            'param_one_time_key': param_one_time_key,
        })
    except:
        return jsonify(message="An error occurred"), 500

@app.route('/compare_one_time_key', methods=['GET'])
def compare_one_time_key():
    try:
        # リクエストされたときのurlを取得する
        url = request.url
        param_one_time_key = request.args.get('one_time_key')

        db_config = {
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
            'database': os.getenv('DATABASE_NAME')   
        }
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("SELECT email, one_time_key FROM one_time_keys where one_time_key = %s;", (param_one_time_key,))
        tables = cursor.fetchall()
        cursor.close()
        cnx.close()

        if param_one_time_key is None:
            return jsonify(message="one_time_key are required : {}".format(url)), 400
        else:
            if tables == []:
                return jsonify(message="one_time_key is not registered"), 400
            if param_one_time_key == tables[0][1]:
                return jsonify({
                    'state': 'success',
                    'email': tables[0][0]
                })
    except:
        return jsonify(message="An error occurred"), 500
    
    
@app.route('/resister_Userinfo', methods=['GET'])
def resister_Userinfo():
    try:
        # リクエストされたときのurlを取得する
        url = request.url
        param_username = request.args.get('username')
        param_password = request.args.get('password')
        param_email_user = request.args.get('email-user')
        param_email_domain = request.args.get('email-domain')

        param_email = param_email_user + "@" + param_email_domain

        db_config = {
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
            'database': os.getenv('DATABASE_NAME')   
        }
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("INSERT INTO users(username, password, email) VALUES(%s, %s, %s);", (param_username, param_password, param_email))
        cnx.commit()

        cursor.execute("SELECT * FROM users where username = %s AND password = %s AND email = %s;", (param_username, param_password, param_email))
        tables = cursor.fetchall()
        cursor.close()
        cnx.close()

        if param_username is None or param_password is None or param_email is None:
            return jsonify(message="username and password are required : {}".format(url)), 400
        else:
            return jsonify({
                'state': 'success',
                'id': tables[0][0],
                'param_username': tables[0][1],
                'param_password': tables[0][2],
                'param_email': tables[0][3],
                'param_created_at': tables[0][4]
            })
    except:
        return jsonify(message="An error occurred"), 500

@app.route('/signIn', methods=['GET'])
def signIn():
    try:
        # リクエストされたときのurlを取得する
        url = request.url
        param_username = request.args.get('username')
        param_password = request.args.get('password')

        db_config = {
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
            'database': os.getenv('DATABASE_NAME')   
        }
        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM users where username = %s AND password = %s;", (param_username, param_password))
        tables = cursor.fetchall()
        cursor.close()
        cnx.close()

        if param_username is None or param_password is None:
            return jsonify(message="username and password are required : {}".format(url)), 400
        else:
            return jsonify({
                'state': 'success',
                'id': tables[0][0],
            })
    except:
        return jsonify(message="An error occurred"), 500
    
@app.route('/getAirocoData', methods=['GET'])
def getAirocoData():
    try:
        # リクエストされたときのurlを取得する
        url = request.url

        db_config = {
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
            'database': os.getenv('DATABASE_NAME')   
        }

        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM sensor_table_R3_401 ORDER BY ABS(TIMESTAMPDIFF(SECOND, time_stamp, NOW())) ASC LIMIT 1;")
        Table = cursor.fetchall()
        cursor.close()
        cnx.close()

        current_Data = {
            'co2': Table[0][2],
            'humidity': Table[0][3],
            'temperature': Table[0][4],
        }

        if Table[0][0] is None:
            return jsonify(message="username and password are required : {}".format(url)), 400
        else:
            return jsonify({
                'state': 'success',
                'co2': current_Data['co2'],
                'humidity': current_Data['humidity'],
                'temperature': current_Data['temperature']
            })
    except:
        return jsonify(message="An error occurred"), 500
    
@app.route('/getAirocoDataForOneWeek', methods=['GET'])
def getAirocoDataForOneWeek():
    try:
        # リクエストされたときのurlを取得する
        url = request.url

        db_config = {
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
            'database': os.getenv('DATABASE_NAME')   
        }
        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM sensor_table_R3_401 ORDER BY ABS(TIMESTAMPDIFF(SECOND, time_stamp, NOW())) ASC LIMIT 3600;")
        Table = cursor.fetchall()
        cursor.close()
        cnx.close()

        Table = np.array(Table)

        # use numpy array  
        current_Data = {
            'co2': Table[:,2],
            'humidity': Table[:,3],
            'temperature': Table[:,4],
        }


        if Table[0][0] is None:
            return jsonify(message="username and password are required : {}".format(url)), 400
        else:
            return jsonify({
                'state': 'success',
                'co2': current_Data['co2'].tolist(),
                'humidity': current_Data['humidity'].tolist(),
                'temperature': current_Data['temperature'].tolist()
            })
    #except:
        #return jsonify(message="An error occurred"), 500
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify(message= str(e) ), 500
    
@app.route('/getflowerData', methods=['GET'])
def getflowerData():
    
    # 正規化された状態IDをもとに、状態を返す
    def returnStatus(status):

        status = str(status)
        status = [int(status[0]), int(status[1])] if len(status) == 2 else [int(status[0])]

        status_dict = {
            0: 'seed',
            1: 'germination',
            2: 'growth',
            3: 'bud',
            4: 'flowering_falf',
            5: 'flowering_full',
        }

        status_abnormal = {
            1: 'wilting',
            2: 'withering',
            3: 'dead',
        }
        #return "safe"
        return status_dict[status[0]] if len(status) == 1 else f'{status_dict[status[0]]}_{status_abnormal[status[1]]}'
    
    try:
        # リクエストされたときのurlを取得する
        url = request.url
        param_username = request.args.get('username')

        if param_username is None:
            return jsonify(message="username and password are required : {}".format(url)), 400


        db_config = {
            'user': os.getenv('DATABASE_USER'),
            'password': os.getenv('DATABASE_PASSWORD'),
            'host': os.getenv('DATABASE_HOST'),
            'database': os.getenv('DATABASE_NAME')   
        }

        
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM flower WHERE user_id = (SELECT id FROM users WHERE username = %s);", (param_username,))
        Table = cursor.fetchall()
        cursor.close()
        cnx.close()

        if Table is None:
            return jsonify(message="username and password are required : {}".format(url)), 400
        else:
            flower_Data = {
                'status': returnStatus(Table[0][1]),
                'water': Table[0][2],
                'fertilizer': Table[0][3],
            }
            return jsonify({
                'state': flower_Data['status'],
                'water': flower_Data['water'],
                'fertilizer': flower_Data['fertilizer'],
            })
    except Exception as e:
        return jsonify(message=f'error -> {str(e)} {Table}'), 500

@app.route('/getBase64', methods=['GET'])
def getBase64():
    try:
        # リクエストされたときのurlを取得する
        url = request.url
        param_imageIndex = request.args.get('imageIndex')

        if param_imageIndex is None:
            return jsonify(message="username and password are required : {}".format(url)), 400
        
        # ./image/test_flower.pngをバイナリファイルとして送信する
        return send_file('./image/test_flower.png', mimetype='image/png')   


        # ./image/test_flower.pngをbase64にエンコードする
        with open(f'./image/test_flower.png', 'rb') as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')

        if base64_image is None:
            return jsonify(message=" we can't create image convert to base64 : {}".format(url)), 400
        else:
            return jsonify({
                'state': 'success',
                'base64_image': base64_image,
            })
    except Exception as e:
        return jsonify(message={str(e)}), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)