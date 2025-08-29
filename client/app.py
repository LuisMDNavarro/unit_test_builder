import os
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv

# Load the API URL from the .env
load_dotenv()
api_url = os.environ.get("API_URL")

# Language options for documentation
language_options = ["Spanish", "English"]
# Testing Framework Options
framework_optios = ["unittest", "pytest"]

# Generates a session_id for the user
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Title and logo alignment
img, title = st.columns([1, 7])
title.title("Unit Test Builder")
img.image("img/python-logo.webp", width=80)
# Displays the session_id
st.write("Session ID:", st.session_state.session_id)
# Aligns the select boxes
col1, col2 = st.columns(2)
language = col1.selectbox("Selecciona tu lenguaje", language_options, index=0)
framework = col2.selectbox(
    "Selecciona un framework para las pruebas:", framework_optios, index=0
)
# Field to write the function that is sent to the API
user_request = st.text_area("Escribe tu funcion:")
# Submit button
send_code = st.button("Enviar")

# If the submit button is pressed
if send_code:
    # Verify that the user_request is not empty
    if user_request.strip():
        # Payload to send
        payload = {
            "session_id": st.session_state.session_id,
            "user_request": user_request,
            "language": language,
            "framework": framework,
        }
        # API request with payload as JSON
        response = requests.post(api_url, json=payload)

        # Check the response status_code
        if response.status_code == 200:
            # Convert the JSON content of the response to a Python object
            data = response.json()
            # Show the response obtained
            api_response = data.get("api_response")
            st.success("Respuesta obtenida exitosamente")
            st.write(api_response)
        elif response.status_code in [400, 404, 429, 500]:
            # Convert the JSON content of the response to a Python object
            data = response.json()
            # Displays the error received
            error = data.get("error")
            st.error(error)
        else:
            # If an unhandled error is received
            st.error("Error al consultar la API")
    else:
        # If user_request is empty
        st.error("Debe escribir una funcion.")
