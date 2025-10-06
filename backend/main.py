from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi import WebSocketDisconnect

app = FastAPI()

active_connections = {}

html = """
<!DOCTYPE html>
<html>
    <body>
        <h1>WebSocket Chat</h1>
        <form onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'></ul>
        <script>
            const userId = 1;
            const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);
            ws.onmessage = (event) => {
                const messages = document.getElementById('messages');
                const li = document.createElement('li');
                li.textContent = event.data;
                messages.appendChild(li);
            };
            function sendMessage(event) {
                const input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = '';
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept() 
    active_connections[user_id] = websocket
    try:
        data = await websocket.receive_text()
        await websocket.send_text(f"Deine Nachricht: {data}")
    except WebSocketDisconnect:
        del active_connections[user_id]






# FastAPI basiert auf Starlette, erweitert diese aber um Komfortabilität, wie OpenAPI-Dokus usw. Die Methoden get(), post() usw. stammen aus der Klasse FastAPI und beinhalten Funktionen, die aus Starlette stammen, weshalb die FastAPI Klasse von der Starlette Klasse erbt. FastAPI und Uvicorn kommunizieren über ein ASGI-Protokoll, meist über Python-Dicsts. Uvicorn kümmert sich um die Netzwerkebene (TCP), nimmt also HTTP-(Upgrade-)Requests entgegen usw. und vermittelt diese über das ASGI an die FastAPI-App. Diese wird dann ausgeführt und führt die dem Request entsprechende Funktion aus. Beispiel @app.websocket("/ws"): Der Client (z. B. Browser) sendet Uvicorn einen HTTP-Upgrade-Request. Diese wird z. B. in ein Python-Dict umgewandelt und über das ASGI an die App übermittelt. Dort steht die Information, dass ein Client eine Websocket-Verbindung aufbauen will. Also erzeugt Starlette ein Objekt bzw. eine Instanz aus der Klasse "WebSocket" und FastAPI leitet sie weiter. Da FastAPI anhand der Informationen, die ihn von Uvicorn bereitgestellt wurden erkennt, dass die aufgerufene URL mit "/ws" endet, ruft er die asynchrone Funktion websocket_endpoint auf und übergibt dieser das vorhin erzeugte Websocket-Objekt. Dieses Objekt beinhaltet Funktionen wie accept() usw. und Informationen zur Verbindung, z. B. Informationen zum Client.