
from google.auth.exceptions import RefreshError
import requests,json
from oauthlib.oauth2 import WebApplicationClient
from flask import request,current_app

def authflow(googleprovider,client):
    code=request.args.get('code')
    token_endpoint=googleprovider['token_endpoint']
    token_url,headers,body=client.prepare_token_request(token_endpoint,auth_response=request.url,redirect_url=request.base_url,code=code)
    token_response=requests.post(token_url,headers=headers,data=body,auth=(current_app.config['GOOGLE_CLIENT_ID'],current_app.config['GOOGLE_CLIENT_SECRET']),)
    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint=googleprovider['userinfo_endpoint']
    uri,headers,body=client.add_token(userinfo_endpoint)
    userinfo_response=requests.get(uri,headers=headers,data=body)
    if userinfo_response.json().get('email_verified'):
        id=userinfo_response.json()['sub']
        email=userinfo_response.json()['email']
        picture=userinfo_response.json()['picture']
        users_name=userinfo_response.json()['given_name']
    else:
         return "User email failed to verify ",400
     
    user_data={'id':id,'email':email,'picture':picture,'username':users_name}
    return user_data