import streamlit as st
import requests
import time
import os
from streamlit_autorefresh import st_autorefresh

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

FASTAPI_URL = f'{BACKEND_URL}'
if 'latest_battle_outcome' not in st.session_state:
    st.session_state['latest_battle_outcome'] = ''

if 'p1_health' not in st.session_state:
    st.session_state['p1_health'] = 0
if 'p1_attack' not in st.session_state:
    st.session_state['p1_attack'] = 0
if 'p1_defence' not in st.session_state:
    st.session_state['p1_defence'] = 0
if 'p1_speed' not in st.session_state:
    st.session_state['p1_speed'] = 0
if 'p1_stamina' not in st.session_state:
    st.session_state['p1_stamina'] = 0

if 'p2_health' not in st.session_state:
    st.session_state['p2_health'] = 0
if 'p2_attack' not in st.session_state:
    st.session_state['p2_attack'] = 0
if 'p2_defence' not in st.session_state:
    st.session_state['p2_defence'] = 0
if 'p2_speed' not in st.session_state:
    st.session_state['p2_speed'] = 0
if 'p2_stamina' not in st.session_state:
    st.session_state['p2_stamina'] = 0

col1, col2, col3 = st.columns([20,40,20])

cards_data = [
    {"id": 1, "title": "yuji itadori", "image": r"C:\Users\ADMIN\Desktop\llm_poke_game\images\yuji_itadori.jpg"},
    {"id": 2, "title": "Megumi Fushiguro", "image": r"C:\Users\ADMIN\Desktop\llm_poke_game\images\megumi_fushiguro.jpg"}
]

# 1. Map names and visuals safely
player_title = "Unknown Attacker"
player_image = "https://placehold.co"
opponent_title = "Unknown Target"
opponent_image = "https://placehold.co..."

for card in cards_data:
    if int(st.session_state.selected_character) == card['id']:
        player_image = card['image']
        player_title = card['title']

# --- Lobby Synchronization Block ---
id_resp = requests.get(url=f'{FASTAPI_URL}/get_opponent/{st.session_state.user_id}')
opponent_id = id_resp.json().get('opponent_id')
opponent_char_id = None

if opponent_id:
    opponent_title = "Loading profile Selection..."
    opponent_image = "https://placehold.co..."
    
    response1 = requests.post(url=f'{FASTAPI_URL}/selected_char', json={'code':st.session_state.code,'player_id': st.session_state.user_id})
    response2 = requests.post(url=f'{FASTAPI_URL}/selected_char', json={'code':st.session_state.code,'player_id': opponent_id})
    if response1.status_code == 200 and response2.status_code == 200:
        player_char_id = response1.json().get('char_id')
        opponent_char_id = response2.json().get('char_id')
        if opponent_char_id is not None:
            for card in cards_data:
                if int(opponent_char_id) == card['id']:
                    opponent_image = card['image']
                    opponent_title = card['title']
                    break
        else:
            if response2.json().get('status') == 'failed':
                st.error('lobby not initilaized')
            else:
                st.error('player not in lobby')


    # 🌟 ADD THIS CRITICAL CALL HERE:
        # initialize only 1 timein backend
        if 'backend_stats_initialized' not in st.session_state:
            init_payload = {
                'code': st.session_state.code
            }
            init_resp = requests.post(url=f'{FASTAPI_URL}/init_stats', json=init_payload)
            if init_resp.status_code == 200:
                #Mark as initialized so it doesn't repeatedly call it on every rerun
                if init_resp.json()['status'] == 'failed':
                    st.error('lobby not initialzed')
                elif init_resp.json()['status'] == 'waiting':
                    st.error('Waiting for other player')
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state['backend_stats_initialized'] = True
                    st.write(init_resp.json())
                    base_stats = init_resp.json().get('player_att')[st.session_state.user_id]
                    oppo_base_stats = init_resp.json().get('player_att')[opponent_id]

                    try:
                        attacker_response = requests.post(  
                            url=f'{FASTAPI_URL}/who_will_attacker', 
                            json={'id': st.session_state.user_id, 'opponent_id': opponent_id,'code':st.session_state.code}  
                        )   

                        if attacker_response.status_code == 200:    
                            backend_attacker = attacker_response.json().get('attacker') 

                            if st.session_state.user_id == backend_attacker:    
                                st.session_state.current_attacker = True    
                                st.subheader("Your Turn")   
                            else:   
                                st.session_state.current_attacker = False   
                                st.subheader("Opponent's Turn") 
                        else:   
                            st.error("Failed to parse match layout status.")    
                    except requests.exceptions.ConnectionError:     
                        st.error("Could not reach backend match synchronizer.") 
            else:
                st.error("Failed to initialize match stats on backend engine.")
                
    else:
        with st.spinner("⏳ Waiting for opponent to load into battle..."):
            time.sleep(1.5)
            st.rerun()
else:
    st.info("Looking for match configurations...")
    time.sleep(2)
    st.rerun()

# --- UI Column Layout Presentation ---

#player turn display
# --- UI Column Layout Presentation ---



# 1. Player Turn Management

st.markdown(
    """
    <style>
        /* Changes the colored moving bar */
        .stProgress > div > div > div > div {
            background-color: #00FF00; /* Green */
        }
        
        /* Optional: Changes the empty/background trail part */
        .stProgress > div > div > div {
            background-color: #FF0000; /* Red */
        }
    </style>
    """,
    unsafe_allow_html=True
)
if 'p1_bar' not in st.session_state:
    st.session_state.p1_bar = st.progress(base_stats.get('curr_health')/base_stats.get('curr_health'))
if 'p2_bar' not in st.session_state:
    st.session_state.p2_bar = st.progress(oppo_base_stats.get('curr_health')/oppo_base_stats.get('curr_health'))

# --- 2. Dynamic Player Turn Management ---
@st.fragment(run_every = 1)
def main_rerun():
    if st.session_state.code is not None:
        try:
            response = requests.post(
                url=f'{FASTAPI_URL}/curr_attacker',
                json={'code': int(st.session_state.code)}
            )
            if response.status_code == 200:
                player_id = response.json().get('output')['current_attacker']

                forth_page = st.Page('frontend_pages/4th_page.py',title='Forth_pages')
                if response.json().get('output')[st.session_state.user_id]['curr_health'] <= 0:
                    requests.post(url=f'{FASTAPI_URL}/winner',json={'code':st.session_state.code,'player_id':st.session_state.user_id})
                    st.switch_page(forth_page)
                elif response.json().get('output')[opponent_id]['curr_health'] <= 0:
                    requests.post(url=f'{FASTAPI_URL}/winner',json={'code':st.session_state.code,'player_id':opponent_id})
                    st.switch_page(forth_page)
                st.session_state.current_attacker = (player_id == st.session_state.user_id)

                st.session_state.p1_health = response.json().get('output')[st.session_state.user_id]['curr_health']/base_stats.get('curr_health')
                st.session_state.p1_attack = response.json().get('output')[st.session_state.user_id]['curr_attack']
                st.session_state.p1_defence = response.json().get('output')[st.session_state.user_id]['curr_defence']
                st.session_state.p1_speed = response.json().get('output')[st.session_state.user_id]['curr_speed']
                st.session_state.p1_stamina = response.json().get('output')[st.session_state.user_id]['curr_stamina'] 

                st.session_state.p2_health = response.json().get('output')[opponent_id]['curr_health']/oppo_base_stats.get('curr_health')
                st.session_state.p2_attack = response.json().get('output')[opponent_id]['curr_attack']
                st.session_state.p2_defence = response.json().get('output')[opponent_id]['curr_defence']
                st.session_state.p2_speed = response.json().get('output')[opponent_id]['curr_speed']
                st.session_state.p2_stamina = response.json().get('output')[opponent_id]['curr_stamina'] 
                st.write("P1 health:", st.session_state.get("p1_health"))
                st.write("P2 health:", st.session_state.get("p2_health"))
                st.write('base_stats:',base_stats.get('curr_health'))
                st.write('curr_health:',response.json().get('output')[st.session_state.user_id]['curr_health'])
            
            else:
                st.session_state.current_attacker = False
        except Exception:
            st.session_state.current_attacker = False

    # --- 3. UI Column Layout Presentation ---
    col1, col2, col3 = st.columns([20, 40, 20])

    
    with col1:
        st.image(player_image, caption=f"You ({player_title})", use_container_width=True)
        st.session_state.p1_bar.progress(st.session_state.p1_health)

    # MIDDLE COLUMN: Actions & Turn Logging
    with col2:
        if st.session_state.current_attacker:
            st.subheader("💥 Execute Your Action") 

            with st.form(key="battle_move_form", clear_on_submit=True): 
                move_query = st.text_area(
                    'What will your character do?', 
                    height=150, 
                    placeholder="Type your strategic action or attack here..."
                )   
                submit_action = st.form_submit_button(label="💥 Commit Move")   

                if submit_action:   
                    if move_query.strip() == "":    
                        st.error("Please describe your move before committing!")    
                    else:   
                        with st.spinner("Analyzing scenario context..."):   
                            attack_payload = {  
                                'code': int(st.session_state.code),
                                "attack": move_query,   
                                'curr_attacker': st.session_state.user_id,
                                "char_id": int(player_char_id)
                            }   

                            try:    
                                battle_response = requests.post(url=f'{FASTAPI_URL}/give_attack', json=attack_payload)  

                                if battle_response.status_code == 200:  
                                    st.success("Action logged successfully!")   
                                    
                                    room = battle_response.json().get('game_room')
                                    

                                    # Update state cache instantly before forcing rerun
                                    st.session_state['latest_battle_outcome'] = battle_response.json().get('prediction')

                                else:   
                                    st.error(
                                    f"Server rejected attack action: "
                                    f"{battle_response.status_code} - {battle_response.text}"
                                    )   
                            except requests.exceptions.ConnectionError: 
                                st.error("Could not reach the backend fight engine.")   
        else:
            st.subheader("⏳ Waiting for Opponent...")
            st.info("The enemy is preparing their strategic movements.")

        # --- 4. Clean Real-time Log Retrieval Pipeline ---
        if st.session_state.code is not None:
            try:
                log_response = requests.post(
                    url=f'{FASTAPI_URL}/get_battle_log',
                    json={'code': int(st.session_state.code)}
                )
                if log_response.status_code == 200:
                    server_log = log_response.json().get('output')

                    if not server_log or "No moves committed yet" in str(server_log):
                        st.session_state['latest_battle_outcome'] = 'The match has just begun! Waiting for first move...'
                
                    else:
                        st.session_state['latest_battle_outcome'] = server_log
            except Exception:
                pass

        # Render history block globally so it remains visible to both players at all times
        if st.session_state.get('latest_battle_outcome'): 
            st.markdown("### 📝 Turn Outcome:") 
            st.info(st.session_state['latest_battle_outcome']) 

    with col3:
        st.image(opponent_image, caption=f"Opponent ({opponent_title})", use_container_width=True)
        st.session_state.p2_bar.progress(st.session_state.p2_health)
main_rerun()  
