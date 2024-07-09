from InstagramBot import InstagramBot
from flask import Flask, request, Response
import requests
import json
import os


igg = InstagramBot()

app = Flask(__name__)

APIKEY = os.environ.get("APIKEY", "564c755e-d24f-41c3-9532-eccd8e061469")
WEBHOOK = os.environ.get("WEBHOOK", "http://localhost:5000/webhook")

@app.route('/create-like', methods=['POST'])
def create_like():
    if ( APIKEY not in request.headers.get("Authorization")):
        response = Response(json.dumps({"message": "User unauthorized."}), status=401, content_type="application/json")
        return response
    
    if request.method == 'POST':
        body = request.get_json()
        
        login: list = body["login"]
        usernames: list = body["usernames"]
        resp_json: str = json.dumps({
            "message": "Processo de curtir fotos iniciado.",
            "usernames": usernames,
            "webhook": WEBHOOK
        })
        response = Response(resp_json, status=201, content_type="application/json")
        
        def on_close():
            results:list = []
            for username in usernames:
                result = igg.run_likes(login=login, username=username)
                results.append(result)
            print(results)
            requests.post(WEBHOOK, {"results": results})
                
        response.call_on_close(on_close)
        
        return response

# PODE RETORNAR UM UUID REFERENTE AO USER_DATA DO USUÁRIO E SALVAR NO EXCEL
@app.route('/create-login', methods=['POST'])
def create_login():
    if ( APIKEY not in request.headers.get("Authorization")):
        response = Response(json.dumps({"message": "User unauthorized."}), status=401, content_type="application/json")
        return response
    
    
    if request.method == 'POST':
        body = request.get_json()
        
        username: str = body["username"]
        password: str = body["password"]
        resp_json: str = json.dumps({
            "message": "Processo de login iniciado.",
            "username": username,
            "webhook": WEBHOOK
        })
        response = Response(resp_json, status=201, content_type="application/json")
        
        def on_close():
            def double_auth_callback(login= username, codeDescription=''):
                requests.post(WEBHOOK, json=json.dumps({
                    "login": username,
                    "codeDescription": codeDescription,
                    "message": "Post the double authetication code.", 
                    "route": "/double-auth"
                }))

            igg.set_login(username, password)
            login = igg.run_login(double_auth_callback=double_auth_callback) 
            
            if (login == False):
                requests.post(WEBHOOK, json=json.dumps({
                    "login": "username",
                    "message": "User are not registered.",
                    "route": "/create-login"
                }))
                
            else:
                requests.post(WEBHOOK, json=json.dumps({
                    "login": username,
                    "message": "Login completed.", 
                    "route": "/create-login"
                }))
                
                
        response.call_on_close(on_close)
        
        return response

@app.route('/webhook', methods=['POST'])
def webhook():
    print(request.get_json())
    return request.get_json()

# @app.route('/get-accounts', methods=['GET'])
# def get_accounts():
#     if ( APIKEY not in request.headers.get("Authorization")):
#         response = Response(json.dumps({"message": "User unauthorized."}), status=401, content_type="application/json")
#         return response
    
#     result = igg.get_accounts()
#     return result

@app.route('/double-auth', methods=['POST'])
def double_auth():
    if ( APIKEY not in request.headers.get("Authorization")):
        response = Response(json.dumps({"message": "User unauthorized."}), status=401, content_type="application/json")
        return response
    
    body = request.get_json()
    login: str = body["login"]
    code: str = body["code"]
    
    igg.save_user_in_db(login=login, code=code)

    resp_json: str = json.dumps({
        "message": "Code registered.",
        "login": login,
        "webhook": WEBHOOK
    })
    
    response = Response(resp_json, status=201, content_type="application/json")
    return response

app.run(host='0.0.0.0', port=5000)