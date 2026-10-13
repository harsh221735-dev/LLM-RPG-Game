import streamlit as st
import requests
import secrets
import time
import os

# Initialize session states
if "user_matched" not in st.session_state:
    st.session_state.user_matched = False
if "code" not in st.session_state:
    st.session_state.code = None



# Fallback to localhost if BACKEND_URL isn't set (like during local development)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

second_page = st.Page("frontend_pages/2nd_page.py", title="Second Page")

# Redirect immediately if matched
if st.session_state.user_matched:
    #try:
    #    requests.post(url='http://127.0.0.1:8000/create_room', json={})
    #except Exception:
    #    pass  # Handle backend offline gracefully

    st.switch_page(second_page)

st.header('Generate code:')
with st.form(key='gen_code'):
    create_code = st.form_submit_button(label='Generate Code')
    
    if create_code:
        generated_code = secrets.randbelow(10000)
        st.session_state.code = generated_code
        
        payload = {'code_set': generated_code, 'user_id': st.session_state.user_id}
        response = requests.post(url=f'{BACKEND_URL}/code_check', json=payload)
        
        if response.status_code == 200 and response.json().get('result') == 'passed':
            st.code(generated_code, language='text')

# Poll for matchmaking status if a code exists
if st.session_state.code:
    timer_text = st.empty()
    timer = 30
    
    while timer > 0:
        timer_text.markdown(f'Time remaining: :red[{timer} seconds]')
        
        # FIX: Sending code as integer to match Pydantic model
        payload = {'code': int(st.session_state.code)}
        try:
            response = requests.post(url=f'{BACKEND_URL}/user_check', json=payload)
            if response.status_code == 200 and response.json().get('result') == 'success':
                st.session_state.user_matched = True
                break
        except Exception:
            st.error("Backend server communication failed.")
            break
            
        time.sleep(1)
        timer -= 1

    if st.session_state.user_matched:
        timer_text.success("Matched! Redirecting...")
        time.sleep(0.5)
        st.rerun()
    else:
        timer_text.error("❌ Matchmaking timed out.")
        st.session_state.code = None # Reset state

st.header('Or Enter Code: ')
with st.form(key='match_code'):
    entered_code = st.number_input('Enter the Code', value=0, step=1)
    matched_code = st.form_submit_button(label='Match Code')
    
    if matched_code:
        payload = {'received_code': int(entered_code), 'user_id': st.session_state.user_id}
        response = requests.post(url=f'{BACKEND_URL}/match_code', json=payload)
        
        if response.status_code == 200 and response.json().get('result') == 'success':
            st.session_state.code = entered_code
            st.session_state.user_matched = True
            st.success("Successfully matched!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error('Failed to match code.')
