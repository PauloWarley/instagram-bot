from InstagramBot import InstagramBot
from flask import Flask, request, Response
import requests
import json

igg = InstagramBot()

app = Flask(__name__)

WEBHOOK = "http://localhost:5000/webhook"

@app.route('/create-like', methods=['POST'])
def create_like():
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
            result = igg.set_login(username, password)
            igg.run_login()
            
            requests.post(WEBHOOK, {"result": result})
                
        response.call_on_close(on_close)
        
        return response

@app.route('/webhook', methods=['POST'])
def webhook():
    print(request.get_json())
    return {}

@app.route('/get-accounts', methods=['GET'])
def get_accounts():
    result = igg.get_accounts()
    return result

app.run()