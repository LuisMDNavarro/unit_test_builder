# flake8: noqa
import json
import uuid

import streamlit as st
import websocket

api_url = "wss://8sgdg5yifg.execute-api.us-east-1.amazonaws.com/$default/"

language_options = ["Spanish", "English"]
framework_optios = ["unittest", "pytest"]

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
img, title = st.columns([1, 7])
title.title("Unit Test Builder")
img.image("img/python-logo.webp", width=80)
st.write("Session ID:", st.session_state.session_id)
col1, col2 = st.columns(2)
language = col1.selectbox("Selecciona tu lenguaje", language_options, index=0)
framework = col2.selectbox(
    "Selecciona un framework para las pruebas:", framework_optios, index=0
)

user_request = st.text_area("Escribe tu funcion:")
send_code = st.button("Enviar")

response_box = st.empty()


def on_message(ws, message):
    try:
        data = json.loads(message)
        print(message)
        if "text" in data:
            print(data["text"])
            current = response_box.text_area(
                "Respuesta del API:",
                value=response_box.text_area("Respuesta del API:").replace("\r", "")
                + data["text"],
                height=400,
            )
    except Exception as e:
        st.error(f"Error procesando mensaje: {e}")


def on_error(ws, error):
    st.error(f"Error en WebSocket: {error}")


def on_close(ws, close_status_code, close_msg):
    st.info("Conexión cerrada")


def on_open(ws):
    payload = {
        "action": "test",
        "session_id": st.session_state.session_id,
        "user_request": user_request,
        "language": language,
        "framework": framework,
    }
    ws.send(json.dumps(payload))


if send_code:
    if user_request.strip():
        ws = websocket.WebSocketApp(
            api_url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )
        ws.run_forever()
        # payload = {
        #    "session_id": st.session_state.session_id,
        #    "user_request": user_request,
        #    "language": language,
        #    "framework": framework,
        # }

        # response = requests.post(api_url, json=payload)

        # if response.status_code == 200:
        #    data = response.json()
        #    api_response = data.get("api_response")
        #    st.success("Respuesta obtenida exitosamente")
        #    st.write(api_response)
        # elif response.status_code in [400, 404, 429, 500]:
        #    data = response.json()
        #    error = data.get("error")
        #    st.error(error)
        # else:
        #    st.error("Error al consultar la API")
        #    data = response.json()
        #    st.write(data)
        #    st.write("Status Code:", response.status_code)
        #    st.write("Headers:", dict(response.headers))
        #    st.text("Contenido (str):")
        #    st.text(response.text)
    else:
        st.error("Debe escribir una funcion.")
