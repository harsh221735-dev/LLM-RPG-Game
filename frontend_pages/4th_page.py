import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

response = requests.post(
                url=f'{BACKEND_URL}/curr_attacker',
                json={'code': int(st.session_state.code)}
            )
if response.status_code == 200:
    player_id = response.json().get('output')['winner']
    if st.session_state.user_id == player_id:
        st.header('Congrats you won!')
    else:
        st.header('You lost LOL!')