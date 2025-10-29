'use strict';

window.addEventListener("DOMContentLoaded", () => {
    const joinDiv = document.getElementById("join-container")

    const form = document.createElement("form");
    joinDiv.append(form);

    const roomNameInput = document.createElement("input");
    roomNameInput.type = "text";
    roomNameInput.placeholder = "Room Name"

    const roomPasswordInput = document.createElement("Input");
    roomPasswordInput.type = "text"
    roomPasswordInput.placeholder = "Password"

    const usernameInput = document.createElement("input");
    usernameInput.type = "text";
    usernameInput.placeholder = "Username";

    const connectButton = document.createElement("button");
    connectButton.textContent = "Connect";

    form.append(roomNameInput, roomPasswordInput,usernameInput, connectButton);

    roomNameInput.addEventListener("keydown", function(event) {
        if (event.key == "keydown") {
            event.preventDefault();
            connectButton.click();
        }
    });

    roomPasswordInput.addEventListener("keydown", function(event) {
        if (event.key == "keydown") {
            event.preventDefault();
            connectButton.click();
        }
    });

    usernameInput.addEventListener("keydown", function(event) {
        if (event.key == "keydown") {
            event.preventDefault();
            connectButton.click();
        }
    });

    connectButton.addEventListener("click", (event) => {
        event.preventDefault();

        joinDiv.style.display = "none";

        const ws = new WebSocket(`ws://localhost:8000/ws/${roomIdInput.value}`);

        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: "join",
                username: usernameInput.value,
                room_name: roomNameInput.value,
                room_password: roomPasswordInput.value
            }));

            const message = document.createElement("input");
            message.type = "text";
            message.placeholder = "Your message...";

            const sendButton = document.createElement("button");
            sendButton.type = "button";
            sendButton.textContent = "Send";

            const chatDiv = document.getElementById("chat-container");

            chatDiv.append(message, sendButton);

            sendButton.addEventListener("click", () => {
                ws.send(JSON.stringify({
                    type: "message",
                    message: message.value,
                    user_name: usernameInput.value
                }));

                const p = document.createElement("p");
                p.textContent = `You: ${message.value}`;
                chatDiv.append(p);
                message.value = "";
            });

            ws.onmessage = (event) => {
                const p = document.createElement("p");
                const eventData = JSON.parse(event.data);
                if (eventData.type === "join") {
                    const username = eventData.user_name;
                    p.textContent = `${username} entered the chat!`;
                    chatDiv.append(p);
                } else if (eventData.type === "message") {
                    const username = eventData.user_name;
                    const message = eventData.message;
                    p.textContent = `${eventData.user_name}: ${eventData.message}`;
                    chatDiv.append(p);
                }
            };
        };
    });
});

