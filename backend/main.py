from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

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
            const ws = new WebSocket("ws://localhost:8000/ws");
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept() # warte bis der WebSocket-Handshake zwischen Server und Client beendet ist 
    while True:
        data = await websocket.receive_text() # warte bis über den Websocket eine Nachricht vom Client eingeht
        await websocket.send_text(f"Du hast gesendet: {data}") # sende data an uvicorn und warte auf die Bestätigung






# FastAPI basiert auf Starlette, erweitert diese aber um Komfortabilität, wie OpenAPI-Dokus usw. Die Methoden get(), post() usw. stammen aus der Klasse FastAPI und beinhalten Funktionen, die aus Starlette stammen, weshalb die FastAPI Klasse von der Starlette Klasse erbt. FastAPI und Uvicorn kommunizieren über ein ASGI-Protokoll, meist über Python-Dicsts. Uvicorn kümmert sich um die Netzwerkebene (TCP), nimmt also HTTP-(Upgrade-)Requests entgegen usw. und vermittelt diese über das ASGI an die FastAPI-App. Diese wird dann ausgeführt und führt die dem Request entsprechende Funktion aus. Beispiel @app.websocket("/ws"): Der Client (z. B. Browser) sendet Uvicorn einen HTTP-Upgrade-Request. Diese wird z. B. in ein Python-Dict umgewandelt und über das ASGI an die App übermittelt. Dort steht die Information, dass ein Client eine Websocket-Verbindung aufbauen will. Also erzeugt Starlette ein Objekt bzw. eine Instanz aus der Klasse "WebSocket" und FastAPI leitet sie weiter. Da FastAPI anhand der Informationen, die ihn von Uvicorn bereitgestellt wurden erkennt, dass die aufgerufene URL mit "/ws" endet, ruft er die asynchrone Funktion websocket_endpoint auf und übergibt dieser das vorhin erzeugte Websocket-Objekt. Dieses Objekt beinhaltet Funktionen wie accept() usw. und Informationen zur Verbindung, z. B. Informationen zum Client.