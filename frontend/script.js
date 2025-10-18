'use strict';

window.addEventListener("DOMContentLoaded", () => {
    const joinDiv = document.getElementById("join-container")

    const form = document.createElement("form");
    joinDiv.append(form);

    const roomInput = document.createElement("input");
    roomInput.type = "text";
    roomInput.placeholder = "Room ID";

    const usernameInput = document.createElement("input");
    usernameInput.type = "text";
    usernameInput.placeholder = "Username";

    const connectButton = document.createElement("button");
    connectButton.textContent = "Connect";

    form.append(roomInput, usernameInput, connectButton);

    connectButton.addEventListener("click", (event) => {
        event.preventDefault();

        joinDiv.style.display = "none";

        const ws = new WebSocket(`ws://localhost:8000/ws/${roomInput.value}`);

        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: "join",
                user_name: usernameInput.value,
                room_id: roomInput.value
            }));

            const message = document.createElement("input");
            message.type ="text";
            message.placeholder = "Your message...";

            const sendButton = document.createElement("button");
            sendButton.type = "button";
            sendButton.textContent = "Send";

            const chatDiv = document.getElementById("chat-container");

            chatDiv.append(message, sendButton);

            sendButton.addEventListener("click", () => {
                ws.send(JSON.stringify({
                    type: "message",
                    message: message.value
                }));

                const p = document.createElement("p");
                p.textContent = `You: ${message.value}`;
                chatDiv.append(p);
                message.value = "";
            });

            ws.onmessage = (event) => {
                const p = document.createElement("p");
                p.textContent = `User: ${event.data}`;
                chatDiv.append(p);
            }
        };
    });
});

