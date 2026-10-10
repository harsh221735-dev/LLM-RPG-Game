import streamlit as st
import database
import requests
import time
if st.session_state.code is not None:
    try:
        url = f"http://127.0.0.1:8000/get_temp_room/{int(st.session_state.code)}"
        response = requests.get(url=url)
        
        # This will now correctly evaluate to False if a 404 happens
        if response.status_code == 200:
            st.write(response.json())
        elif response.status_code == 404:
            st.warning(response.json()['detail'])  # Reads the HTTPException detail
        else:
            st.error("An unexpected server error occurred.")
    except Exception as e:
        st.error(f"Connection failed: {e}")

# 1. Initialize states safely
if 'waiting_for_match' not in st.session_state:
    st.session_state.waiting_for_match = False
if 'start_battle' not in st.session_state:
    st.session_state.start_battle = False
if 'match_timer' not in st.session_state:
    st.session_state.match_timer = 20

# FIX: Track if this run is an explicit manual browser refresh pass. 
# If it is, kill any lingering ghost matchmaking flags.
if "page_loaded" not in st.session_state:
    st.session_state.page_loaded = True
    st.session_state.waiting_for_match = False  # Hard reset queue on refresh

st.title("Choose Your Character")

third_page = st.Page('frontend_pages/3rd_page.py', title='Third page')
if st.session_state.start_battle:
    #requests.post(url='http://127.0.0.1:8000/upload_char',json={'player_id': st.session_state.user_id,'char_id':st.session_state.selected_character})
    requests.post(url='http://127.0.0.1:8000/lobby',json={'code': st.session_state.code,'player_id':st.session_state.user_id,'char_id':st.session_state.selected_character})
    st.switch_page(third_page)

cards_data = [
    {"id": 1, "title": "yuji itadori", "image": r"C:\Users\ADMIN\Desktop\llm_poke_game\images\yuji_itadori.jpg"},
    {"id": 2, "title": "Megumi Fushiguro", "image": r"C:\Users\ADMIN\Desktop\llm_poke_game\images\megumi_fushiguro.jpg"}
]

cols = st.columns(len(cards_data))
for index, card in enumerate(cards_data):
    with cols[index]:
        with st.container(border=True):
            st.image(card['image'], use_container_width=True)
            st.subheader(card['title'])
          
        if st.button(f'Select {card["title"]}', key=card['id'], use_container_width=True):
            st.session_state.selected_character = card['id']
            st.success(f'You chose {card["title"]}')

payload = {'player_id': st.session_state.user_id}

if st.session_state.get('selected_character'):                                   
    response = requests.get(url=f'http://127.0.0.1:8800/database/{st.session_state.selected_character}')
    
    # Check if Flask successfully found the player
    if response.status_code == 200:
        data_json = response.json()
        result = data_json['output']                                             
        st.info(f"Attack: {result[3]}")                                              
        st.info(f"Defence: {result[4]}")                                             
        st.info(f"Speed: {result[5]}")
    else:
        # This will show you exactly what Flask's database query complained about
        try:
            error_msg = response.json().get('error', 'Unknown server error')
        except Exception:
            error_msg = response.text
        st.error(f"Error from database: {error_msg}")

    
    with st.form(key='battle_start'):
        battle = st.form_submit_button(label='Start Battle')
        
    if battle:
        response = requests.post(url='http://127.0.0.1:8000/assigning_players', json=payload)
        if response.json().get('status') == 'joined':    
            st.session_state.start_battle = True 
            st.rerun()   
        else:
            # ONLY turn the countdown engine on right here when clicked!
            st.session_state.waiting_for_match = True
            st.session_state.match_timer = 20  
            st.rerun()

# This block will now stay completely quiet unless 'battle' was explicitly pressed
if st.session_state.waiting_for_match and not st.session_state.start_battle:
    timer_text = st.empty()
    
    if st.session_state.match_timer > 0:
        timer_text.markdown(f'Waiting for player. Time remaining: :red[{st.session_state.match_timer} seconds]')
        
        try:
            response = requests.post(url='http://127.0.0.1:8000/assigning_players', json=payload)        
            if response.json().get('status') == 'joined':       
                st.session_state.start_battle = True 
                st.session_state.waiting_for_match = False
                timer_text.success("Match Found! Transitioning to battle arena...")
                time.sleep(0.5)
                st.rerun()
        except Exception:
            pass
            
        time.sleep(1)
        st.session_state.match_timer -= 1
        st.rerun()
    else:
        st.session_state.waiting_for_match = False
        requests.post(url='http://127.0.0.1:8000/leave_queue', json=payload)
        timer_text.error('Matchmaking timed out. Please try again.')
