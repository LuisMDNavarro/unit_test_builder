import uuid

import requests
import streamlit as st

api_url = "https://xbs8wejgm4.execute-api.us-east-1.amazonaws.com/generate-test"

language_options = ["Spanish", "English"]
framework_optios = ["unittest", "pytest"]

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("Unit Test Builder")
st.write("Session ID:", st.session_state.session_id)
col1, col2 = st.columns(2)
language = col1.selectbox("Selecciona tu lenguaje", language_options, index=0)
framework = col2.selectbox(
    "Selecciona un framework para las pruebas:", framework_optios, index=0
)

user_request = st.text_area("Escribe tu funcion:")
send_code = st.button("Enviar")

if send_code:
    if user_request.strip():
        payload = {
            "session_id": st.session_state.session_id,
            "user_request": user_request,
            "language": language,
            "framework": framework,
        }
        response = requests.post(api_url, json=payload)

        if response.status_code == 200:
            data = response.json()
            api_response = data.get("api_response")
            st.success("Respuesta obtenida exitosamente")
            st.write(api_response)
        elif response.status_code in [400, 404, 429, 500]:
            data = response.json()
            error = data.get("error")
            st.error(error)
        else:
            st.error("Error al consultar la API")
    else:
        st.error("Debe escribir una funcion.")
