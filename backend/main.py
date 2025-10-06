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





