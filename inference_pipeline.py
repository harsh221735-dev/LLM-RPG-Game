import load_models
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import time
import requests
import random
from fastapi import FastAPI, HTTPException
import regex as re
import json
import os
import groq
from groq import Groq

db = load_models.loaded_models()

load_dotenv()
app = FastAPI()

fixed_player1 = {}


fixed_player2 = {}



user_buffer = set()
game_room = {-1:None}
battle_log =  {-1:[]}
temp_room = {}
active_rooms = {}
characters = {}
lobby = {}


class roomPayload(BaseModel):
    code: int
    char_id: int
    player_id: str

@app.post('/lobby')
def lob(payload: roomPayload):
    global lobby
    if payload.code not in lobby:
        lobby[payload.code] = {f'{payload.player_id}':payload.char_id}
    else:
        lobby[payload.code].update({f'{payload.player_id}':payload.char_id})


class IdPayload(BaseModel):
    code: int


@app.post('/init_stats')
def get_charachter(payload: IdPayload):
    # 1. Fetch matching active room state variables from global/state parameters if needed
    # For this function, we pull IDs directly from the incoming payload
    code = payload.code
    if code not in lobby:
        return {'status':'failed'}

    if len(lobby[code]) < 2:
        return {'status':'waiting'}
    
    ids = list(lobby[payload.code].keys())
    player1_id = ids[0]
    player1_char_id = lobby[payload.code][player1_id]
    player2_id = ids[1]
    player2_char_id = lobby[payload.code][player2_id]
    
    selected_char = {}
    opponent = {}
    
    # 2. FIX: Call the database function TWICE separately using 1 argument each
    player_data = requests.get(url=f'http://127.0.0.1:8800/database/{player1_char_id}')
    opponent_data = requests.get(url=f'http://127.0.0.1:8800/database/{player2_char_id}')
    

    selected_char['player_id']   = player_data.json()['output'][0]      
    selected_char['player_name']   = player_data.json()['output'][1]        
    selected_char['curr_health']   = player_data.json()['output'][2]        
    selected_char['curr_attack']   = player_data.json()['output'][3]        
    selected_char['curr_defence']  = player_data.json()['output'][4]        
    selected_char['curr_speed']    = player_data.json()['output'][5]        
    selected_char['curr_stamina']  = player_data.json()['output'][6]        

    opponent['player_id']   = opponent_data.json()['output'][0] 
    opponent['player_name']   = opponent_data.json()['output'][1]   
    opponent['curr_health']   = opponent_data.json()['output'][2]   
    opponent['curr_attack']   = opponent_data.json()['output'][3]   
    opponent['curr_defence']  = opponent_data.json()['output'][4]   
    opponent['curr_speed']    = opponent_data.json()['output'][5]   
    opponent['curr_stamina']  = opponent_data.json()['output'][6]   

    game_room[code] = {f'{player1_id}':selected_char,f'{player2_id}':opponent,'current_attacker':None,'player1_id':player1_id,'player2_id':player2_id,'winner':None}  


    return {
        "status": "success", 
        "player_att": game_room[code]
    }

# 1. State Store to track the current active attacker ID globally across endpoints
game_state = {
    "current_attacker_id": None
}

class CurrAttackerPayload(BaseModel):
    id: str
    opponent_id: str
    code: int

@app.post('/who_will_attacker')
def get_current_attacker(payload: CurrAttackerPayload):
    # Initialize turn only if the game just started or hasn't been set yet
    if payload.code in game_room:
        game_room[payload.code]['current_attacker'] = random.choice([payload.id, payload.opponent_id])
    
    return {'attacker': game_room[payload.code]['current_attacker']}


TURN_TIME = 30
class curr_attacker_payload(BaseModel):
    code: int
@app.post('/curr_attacker')
def curr_attacker(payload: curr_attacker_payload):
    global game_room

    if payload.code not in game_room:
        raise HTTPException(
            status_code=404,
            detail="Game room not found."
        )

    return {
        'output': game_room[payload.code],
    }

class AttackPayload(BaseModel):
    code: int
    attack: str    
    curr_attacker: str  #user id
    char_id:int

from typing import Dict

# Track active queueing players with their last known timestamp {player_id: timestamp}


@app.post('/give_attack')
def process_attack(payload: AttackPayload):
    
    query = payload.attack
    '''if payload.curr_attacker not in characters:
        raise HTTPException(status_code=400, detail="Invalid player")'''

    if payload.curr_attacker not in active_rooms:
        raise HTTPException(status_code=400, detail="Opponent not found")

    #current_attacker_name = characters[payload.curr_attacker]
    for i in list(lobby[payload.code].keys()):
        if i != payload.curr_attacker:
            opponent_id = i
    
    current_opponent_name = lobby[payload.code][opponent_id]

    player_data = requests.get(url=f'http://127.0.0.1:8800/database/{payload.char_id}')
    opponent_data = requests.get(url=f'http://127.0.0.1:8800/database/{current_opponent_name}')
        

    curr_name = player_data.json()['output'][1] 
    curr_health   = player_data.json()['output'][2]        
    curr_attack   = player_data.json()['output'][3]        
    curr_defence  = player_data.json()['output'][4]        
    curr_speed   = player_data.json()['output'][5]        
    curr_stamina  = player_data.json()['output'][6]        

    oppo_curr_name = opponent_data.json()['output'][1] 
    oppo_curr_health   = opponent_data.json()['output'][2]   
    oppo_curr_attack   = opponent_data.json()['output'][3]   
    oppo_curr_defence  = opponent_data.json()['output'][4]   
    oppo_curr_speed    = opponent_data.json()['output'][5]   
    oppo_curr_stamina  = opponent_data.json()['output'][6]   
    

    print('success 1')

              

    # Retriever Logic
    retriever = db.as_retriever(            
        search_type='similarity_score_threshold',
        search_kwargs={'k': 1, 'score_threshold': 0.3}         
    )           
    relevant_docs = retriever.invoke(query)          
    
    # FIX 1: Removed the duplicated crash-prone statement and wrapped safely
    context = relevant_docs[0].page_content if relevant_docs else "Standard physical confrontation environment."



    def get_attributes(current, base):
        if current <= 0.25 * base:     
            return 'very very low'      
        elif current <= 0.5 * base:        
            return 'very low'       
        elif current <= 0.75 * base:       
            return 'low'        
        elif current <= base:        
            return 'normal'     
        else:       
            return 'high'   
    
    attacker_attack_chng  = get_attributes(game_room[payload.code][payload.curr_attacker]['curr_attack'], curr_attack)
    attacker_defence_chng = get_attributes(game_room[payload.code][payload.curr_attacker]['curr_defence'], curr_defence)
    attacker_speed_chng   = get_attributes(game_room[payload.code][payload.curr_attacker]['curr_speed'], curr_speed)
    attacker_stamina_chng = get_attributes(game_room[payload.code][payload.curr_attacker]['curr_stamina'], curr_stamina)

    opponent_attack_chng  = get_attributes(game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_attack'], oppo_curr_attack)
    opponent_defence_chng = get_attributes(game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_defence'], oppo_curr_defence)
    opponent_speed_chng   = get_attributes(game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_speed'], oppo_curr_speed)
    opponent_stamina_chng = get_attributes(game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_stamina'], oppo_curr_stamina)

    prompt_eg = ""
    # Build Prompt
    prompt = f"<|im_start|>system\nYou are a smart next scenario predictor of a versus battle game and analyze wheather the attack will affect the opponent or not.<|im_end|>\n<|im_start|>user\n'just give next scenario prediction in under 20 words and change in current attributes of attacker and opponent in positive numbers for decrease in attributes in opponent and attacker in percentage but dont include sign by carefully analyzing all parameters strictly in the format:{{\"prediction\": \"...\", \"change_in_attacker_attributes\": {{\"attack\":,\"defence\":,\"speed\":,\"stamina\":}},\"change_in_opponent_attributes\":{{\"attack\":,\"defence\":,\"speed\":,\"health\":}}}};(note: numbers are negetive for atrribute decrese like stamina decreased and positive for attribute increase like regeneration) attacker: {curr_name} ,attacker_attributes :[attack={attacker_attack_chng},stamina={attacker_stamina_chng},speed={attacker_speed_chng}]; opponent: {current_opponent_name} ,opponent_attributes :[health={game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_health']},speed={opponent_speed_chng},def={opponent_defence_chng}],{curr_name}'s_attack:{query},attacker's attack_info:{context},attribute_behaviour-'effects occur all time:attack consumes stamina based on its power, effects occur based on attack:depends on type and power of attack'.<|im_end|>\n<|im_start|>assistant\n"
   
    client = Groq()
# The SDK automatically looks for the GEMINI_API_KEY environment variable
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}]
        )
    # If successful, return the text content
        return {"status": "success", "narration": response.choices[0].message.content}

    except groq.RateLimitError as e:
        # This catches Groq's official 429 Rate Limit error explicitly
        raise HTTPException(
            status_code=429, 
            detail="Rate limit hit! Groq's free tier is overloaded. Try again in a minute."
        )
    
        
    result = response.choices[0].message.content
    # LLM Execution
    '''output = llm(prompt, max_tokens=128, stop=["<|im_end|>"], echo=False)           
    result = output['choices'][0]['text']
    result = response.text'''

    print('result',result)
    #json_result = json.loads(result)
    #print('json:',json_result)

    '''prediction = json_result['prediction']
    change_in_attacker_attributes = json_result['change_in_attacker_attributes']
    change_in_opponent_attributes = json_result['change_in_opponent_attributes']
    print('type:',type(change_in_opponent_attributes.get('health')))'''

    # use regex instead
    prediction_match = re.search(r'"prediction"\s*:\s*"([^"]+)"', result)
    attacker_match = re.search(r'"change_in_attacker_attributes"\s*:\s*\{([^}]+)\}', result)
    opponent_match = re.search(r'"change_in_opponent_attributes"\s*:\s*\{([^}]+)\}', result)

    # Helper function to extract individual key-value stats inside the brackets
    def extract_stats(block_text):
        if not block_text:
            return {}
        # Finds "key": value or 'key': value, even if numbers are negative
        pairs = re.findall(r'["\'](\w+)["\']\s*:\s*(-?\d+)', block_text)
        return {key: int(val) for key, val in pairs}

    # 2. Parse out the data
    prediction = prediction_match.group(1) if prediction_match else None
    change_in_attacker_attributes = extract_stats(attacker_match.group(1)) if attacker_match else {}
    change_in_opponent_attributes = extract_stats(opponent_match.group(1)) if opponent_match else {}

    # Print Results
    print(f"Prediction: {prediction}")
    print(f"Attacker Attributes: {change_in_attacker_attributes}")
    print(f"Opponent Attributes: {change_in_opponent_attributes}")
    # Accessing individual values safely:
    print(f"Opponent Health: {change_in_opponent_attributes.get('health', 0)}")
 
    #prediction = json_result['prediction']
    

    game_room[payload.code][payload.curr_attacker]['curr_health'] = game_room[payload.code][payload.curr_attacker]['curr_health'] + int(change_in_attacker_attributes.get('health','0'))
    game_room[payload.code][payload.curr_attacker]['curr_attack'] = game_room[payload.code][payload.curr_attacker]['curr_attack'] + int(change_in_attacker_attributes.get('attack',0))
    game_room[payload.code][payload.curr_attacker]['curr_defence'] = game_room[payload.code][payload.curr_attacker]['curr_defence'] + int(change_in_attacker_attributes.get('defence',0))
    game_room[payload.code][payload.curr_attacker]['curr_speed']   = game_room[payload.code][payload.curr_attacker]['curr_speed'] + int(change_in_attacker_attributes.get('speed',0))
    game_room[payload.code][payload.curr_attacker]['curr_stamina'] = game_room[payload.code][payload.curr_attacker]['curr_stamina'] + int(change_in_attacker_attributes.get('stamina',0))

    print('before:',game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_health'])
    game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_health'] = game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_health'] + int(change_in_opponent_attributes.get('health',0))
    game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_attack']  = game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_attack'] + int(change_in_opponent_attributes.get('attack',0))
    game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_defence'] = game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_defence'] + int(change_in_opponent_attributes.get('defence',0))
    game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_speed']   = game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_speed'] + int(change_in_opponent_attributes.get('speed',0))
    game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_stamina'] = game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_stamina'] + int(change_in_opponent_attributes.get('stamina',0))

    print('before:',game_room[payload.code][active_rooms[payload.curr_attacker]]['curr_health'])
    # FIX 2: Safely pass turn alternation based on tracking context matching strings
    game_room[payload.code]['current_attacker'] = active_rooms[payload.curr_attacker]
    if payload.code not in battle_log:
        battle_log[payload.code] = []
    battle_log[payload.code].append(prediction)
    if len(battle_log[payload.code]) > 1:
        battle_log[payload.code].pop(0)
    return {
        'prediction': prediction,
        'game_room': game_room,
        'oppo_base_stats': [oppo_curr_health,oppo_curr_attack,oppo_curr_defence,oppo_curr_speed,oppo_curr_stamina],
        'player_base_stats': [curr_health,curr_attack, curr_defence, curr_speed,curr_stamina]
    }

class winner_payload(BaseModel):
    code: int
    player_id: str
@app.post('/winner')
def weiner(payload:winner_payload):
    game_room[payload.code]['winner'] = payload.player_id

class batt_log(BaseModel):
    code: int
@app.post('/get_battle_log')
def get_log(payload:batt_log):
    if payload.code in battle_log:
        return {'output':battle_log.get(payload.code)}
    else:
        return {'output':[]}

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


@app.get('/get_temp_room/<room_code>')
def get_room(room_code):
    return {'result':temp_room[room_code]}

@app.post('/init_players_set')
def set_player():
    global player_set

class assign_payload(BaseModel):
    player_id: str

from typing import Dict

# Track active queueing players with their last known timestamp {player_id: timestamp}
waiting_pool: Dict[str, float] = {}

# Symmetrically maps Player ID -> Opponent Player ID


class AssignPayload(BaseModel):
    player_id: str

@app.post('/assigning_players')
def assign(payload: AssignPayload):
    pid = payload.player_id
    current_time = time.time()
    
    # 1. If this player is already inside a matched room, report success instantly
    if pid in active_rooms:
        return {'status': 'joined'}
        
    # 2. HOUSEKEEPING: Remove any dead ghost players who haven't polled in over 3 seconds
    # This automatically cleans up players who refreshed or closed their tab!
    dead_players = [p for p, t in waiting_pool.items() if current_time - t > 3.0]
    for p in dead_players:
        waiting_pool.pop(p, None)
        
    # 3. Register or update this player's active heartbeat timestamp
    waiting_pool[pid] = current_time
        
    # 4. Check if there is another valid waiting opponent in the pool
    # Filter out our own ID to find a true matchmaking peer
    opponents = [p for p in waiting_pool.keys() if p != pid]
    
    if len(opponents) >= 1:
        opponent_id = opponents[0]
        
        # Pull both cleanly out of the waiting matchmaking pool
        waiting_pool.pop(pid, None)
        waiting_pool.pop(opponent_id, None)
        
        # Link them symmetrically into an active match instance
        active_rooms[pid] = opponent_id
        active_rooms[opponent_id] = pid
        
        return {'status': 'joined'}
        
    return {'status': 'waiting'}

@app.post('/leave_queue')
def leave_queue(payload: assign_payload):
    if payload.player_id in waiting_pool:
        waiting_pool.remove(payload.player_id)
    return {'status': 'removed'}

# Add this endpoint to your backend file
@app.get('/get_opponent/{player_id}')
def get_opponent(player_id: str):
    # active_rooms maps your player_id -> opponent_id
    if player_id in active_rooms:
        return {'status': 'success', 'opponent_id': active_rooms[player_id]}
    return {'status': 'error', 'message': 'Match room not found'}


class up_char(BaseModel):
    player_id: str
    char_id : int
@app.post('/upload_char')
def get_char(payload:up_char):
    global characters
    # active_rooms maps your player_id -> opponent_id
    characters[payload.player_id] = payload.char_id
    print(characters)

class select_char(BaseModel):
    code: int
    player_id: str
@app.post('/selected_char')
def get_char(payload: select_char):

    if payload.code not in lobby:
        return {'status': 'failed', 'char_id': None}

    if payload.player_id not in lobby[payload.code]:
        return {'status': 'waiting', 'char_id': None}

    return {
        'status': 'success',
        'char_id': lobby[payload.code][payload.player_id]
    }

@app.get('/get_temp_room/{room_code}')
def get_room(room_code: int):
    if room_code in temp_room:
        return {'result': temp_room[room_code]} 
    return {'result': 'room not found'}, 404


         
