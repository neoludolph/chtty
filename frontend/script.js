'use strict';

window.addEventListener("DOMContentLoaded", () => {
    const createAndJoinDiv = document.getElementById("join-container")

    // Formular zum Erstellen eines Rooms 
    const createForm = document.createElement("form");
    createAndJoinDiv.append(createForm);

    const createFormHeading = document.createElement("h2");
    createFormHeading.textContent = "Create room";

    const roomNameInputCreate = document.createElement("input");
    roomNameInputCreate.type = "text";
    roomNameInputCreate.placeholder = "Room Name";

    const roomPasswordInputCreate = document.createElement("Input");
    roomPasswordInputCreate.type = "text";
    roomPasswordInputCreate.placeholder = "Password (optional)";

    const usernameInputCreate = document.createElement("input");
    usernameInputCreate.type = "text";
    usernameInputCreate.placeholder = "Your username";

    const createButton = document.createElement("button");
    createButton.textContent = "Create Room";
    createButton.classList.add("button");

    createForm.append(
        createFormHeading, 
        roomNameInputCreate, 
        roomPasswordInputCreate, 
        usernameInputCreate, 
        createButton
    );

    // Formular zum Beitreten eines Rooms
    const joinForm = document.createElement("form");
    createAndJoinDiv.append(joinForm);

    const joinFormHeading = document.createElement("h2");
    joinFormHeading.textContent = "Join room";

    const roomNameInputJoin = document.createElement("input");
    roomNameInputJoin.type = "text";
    roomNameInputJoin.placeholder = "Room Name";

    const roomPasswordInputJoin = document.createElement("Input");
    roomPasswordInputJoin.type = "text";
    roomPasswordInputJoin.placeholder = "Password (optional)";

    const usernameInputJoin = document.createElement("input");
    usernameInputJoin.type = "text";
    usernameInputJoin.placeholder = "Your username";

    const connectButton = document.createElement("button");
    connectButton.textContent = "Connect";
    connectButton.classList.add("button");

    joinForm.append(
        joinFormHeading, 
        roomNameInputJoin, 
        roomPasswordInputJoin, 
        usernameInputJoin, 
        connectButton
    );

    // Formular zum Löschen eines Rooms
    const deleteForm = document.createElement("form");
    createAndJoinDiv.append(deleteForm);

    const deleteFormHeading = document.createElement("h2");
    deleteFormHeading.textContent = "Delete room";

    const roomNameInputDelete = document.createElement("input");
    roomNameInputDelete.type = "text";
    roomNameInputDelete.placeholder = "Room Name";

    const roomPasswordInputDelete = document.createElement("Input");
    roomPasswordInputDelete.type = "text";
    roomPasswordInputDelete.placeholder = "Password (optional)";

    const usernameInputDelete = document.createElement("input");
    usernameInputDelete.type = "text";
    usernameInputDelete.placeholder = "Your username";
    
    const deleteRoomButton = document.createElement("button");
    deleteRoomButton.textContent = "Delete Room";
    deleteRoomButton.classList.add("button");

    const roomId = document.createElement("input");
    roomId.type = "text";
    roomId.placeholder = "Room Id";

    deleteForm.append(
        deleteFormHeading, 
        roomNameInputDelete, 
        roomPasswordInputDelete, 
        usernameInputDelete, 
        roomId,
        deleteRoomButton
    );

    // Keydown für Create-Inputs
    roomNameInputCreate.addEventListener("keydown", function(event) {
        if (event.key == "keydown") {
            event.preventDefault();
            connectButton.click();
        }
    });

    roomPasswordInputCreate.addEventListener("keydown", function(event) {
        if (event.key == "keydown") {
            event.preventDefault();
            connectButton.click();
        }
    });

    usernameInputCreate.addEventListener("keydown", function(event) {
        if (event.key == "keydown") {
            event.preventDefault();
            connectButton.click();
        }
    });

    // Keydown für Join-Inputs
    

    createButton.addEventListener("click", (event) => {
        event.preventDefault();

        fetch('http://localhost:8000/create-room', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                roomname: roomNameInputCreate.value,
                password: roomPasswordInputCreate.value,
                username: usernameInputCreate.value,
            })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("message").textContent = data.message;
            document.getElementById("room_id").textContent = "Room ID: " + data.room_id;
        })
        .catch(error => console.error('Error: ', error));
    });

    deleteRoomButton.addEventListener("click", (event) => {
        event.preventDefault();

        fetch("http://localhost:8000/delete-room", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                room_id: roomId.value,
                password: roomPasswordInputCreate.value,
            })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("message").textContent = data.message;
        })
        .catch(error => console.error('Error: ', error));
    });

    connectButton.addEventListener("click", (event) => {
        event.preventDefault();

        createAndJoinDiv.style.display = "none";

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

