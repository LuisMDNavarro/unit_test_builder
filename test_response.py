# flake8: noqa
import json

import websocket

# URL de tu WebSocket API
ws_url = "wss://8sgdg5yifg.execute-api.us-east-1.amazonaws.com/$default/"


def on_message(ws, message):
    print("Mensaje recibido del servidor:")
    print(message)


def on_error(ws, error):
    print("Error:")
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("Conexión cerrada")


def on_open(ws):
    print("Conexión abierta")
    # Enviar un mensaje al WebSocket
    payload = {
        "action": "test",  # Nombre de la ruta que creaste
        "data": "Hola desde cliente",
        "session_id": "123456789",
        "user_request": "Hola",
        "language": "Spanish",
        "framework": "pytest",
    }
    ws.send(json.dumps(payload))


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.run_forever()
