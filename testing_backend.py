from fastapi import FastAPI
import time
from dotenv import load_dotenv
from pydantic import BaseModel
#import secrets

load_dotenv()
app = FastAPI()

temp_room = {}
codes = set()
class gen_code(BaseModel):
    code_set:int
    user_id:str
@app.post('/code_check')
def gen_code(payload:gen_code):
    global codes
    code = payload.code_set
    if code not in codes:
        temp_room[code] = {payload.user_id}
        codes.add(code)
        return {'result':'passed'}
    else:
        return {'result':'failed'}

class user_payload(BaseModel):
    code:int
@app.post('/user_check')
def user_check(payload:user_payload):
    if payload.code in temp_room and len(temp_room[payload.code]) >= 2:
        return {'result':'success'}
    else:
        return {'result':'failed'}

class code_payload(BaseModel):
    received_code:int
    user_id:str
@app.post('/match_code')
def code_match(payload:code_payload):
    global codes,temp_room
    received_code = payload.received_code
    if received_code in temp_room:
        #adding user to tempp room
        temp_room[received_code].add(payload.user_id)
        codes.remove(received_code)
        return {'result':'success'}
    else:
        return {'result':'failed'}

# FIX: Use a path parameter {room_code} instead of a GET request payload body
@app.get('/get_temp_room/{room_code}')
def get_room(room_code: int):
    if room_code in temp_room:
        return {'result': temp_room[room_code]} 
    return {'result': 'room not found'}, 404
