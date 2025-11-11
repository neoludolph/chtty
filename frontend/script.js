'use strict';

window.addEventListener("DOMContentLoaded", () => {
    const menuContainer = document.getElementById("menu-container");
    
    const roomNameCreate = document.getElementById("room-name-create");
    const roomNameJoin = document.getElementById("room-name-join");
    const roomNameDelete = document.getElementById("room-name-delete");

    const passwordCreate = document.getElementById("password-create");
    const passwordJoin = document.getElementById("password-join");
    const passwordDelete = document.getElementById("password-delete");

    const usernameCreate = document.getElementById("username-create");
    const usernameJoin = document.getElementById("username-join");
    const usernameDelete = document.getElementById("username-delete");

    const roomId = document.getElementById("room-id");

    const createButton = document.getElementById("create-button");
    const connectButton = document.getElementById("connect-button");
    const deleteButton = document.getElementById("delete-button");

    usernameCreate.addEventListener("keydown", function (event) {
        if (event.key == "Enter") {
            event.preventDefault();
            createButton.click();
        }
    });

    usernameJoin.addEventListener("keydown", function (event) {
        if (event.key == "Enter") {
            event.preventDefault();
            connectButton.click();
        }
    });

    usernameDelete.addEventListener("keydown", function (event) {
        if (event.key == "Enter") {
            event.preventDefault();
            deleteButton.click();
        }
    });

    // Creates a room
    createButton.addEventListener("click", (event) => {
        event.preventDefault();

        fetch('http://localhost:8000/create-room', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                roomname: roomNameCreate.value,
                password: passwordCreate.value,
                username: usernameCreate.value,
            })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("message").textContent = data.message;
            document.getElementById("room_id").textContent = "Room ID: " + data.room_id;
        })
        .catch(error => console.error('Error: ', error));
    });

    // Deletes a room
    deleteButton.addEventListener("click", (event) => {
        event.preventDefault();

        fetch("http://localhost:8000/delete-room", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: roomId.value,
                password: passwordCreate.value,
            })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("message").textContent = data.message;
        })
        .catch(error => console.error('Error: ', error));
    });

    // Connects with room
    connectButton.addEventListener("click", (event) => {
        event.preventDefault();

        menuContainer.style.display = "none";

        const ws = new WebSocket(`ws://localhost:8000/ws/${roomNameInputCreate.value}`);

        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: "join",
                username: usernameInputCreate.value,
                roomName: roomNameInputCreate.value,
                roomPassword: roomPasswordInputCreate.value
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
                    userName: usernameInputCreate.value
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

