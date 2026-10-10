import streamlit as st
import requests

response = requests.post(
                url='http://127.0.0.1:8000/curr_attacker',
                json={'code': int(st.session_state.code)}
            )
if response.status_code == 200:
    player_id = response.json().get('output')['winner']
    if st.session_state.user_id == player_id:
        st.header('Congrats you won!')
    else:
        st.header('You lost LOL!')