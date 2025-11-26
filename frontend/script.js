'use strict';

window.addEventListener("DOMContentLoaded", () => {
    const menuContainer = document.getElementById("menu-container-id");

    const roomNameCreate = document.getElementById("room-name-create");
    const roomNameJoin = document.getElementById("room-name-join");
    const roomNameDelete = document.getElementById("room-name-delete");

    const passwordCreate = document.getElementById("password-create");
    const passwordJoin = document.getElementById("password-join");
    const passwordDelete = document.getElementById("password-delete");

    const usernameJoin = document.getElementById("username-join");

    const createButton = document.getElementById("create-button");
    const connectButton = document.getElementById("connect-button");
    const deleteButton = document.getElementById("delete-button");

    function appendMessage(messageArea, username, chatMessage, timestamp) {
        const date = timestamp ? new Date(timestamp) : new Date();
        const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const p = document.createElement("p");
        p.textContent = `${timeString} ${username}: ${chatMessage}`;
        messageArea.append(p);
    }

    passwordCreate.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            createButton.click();
        }
    });

    usernameJoin.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            connectButton.click();
        }
    });

    passwordDelete.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            deleteButton.click();
        }
    });

    // Creates a room
    createButton.addEventListener("click", (event) => {
        event.preventDefault();

        const MessageDiv = document.getElementById("create-message");
        const p = document.createElement("p");

        if (roomNameCreate.value === "" || passwordCreate.value === "") {
            p.textContent = "Please fill in all fields!";
            MessageDiv.textContent = "";
            MessageDiv.append(p); 
            return;
        }

        fetch('http://localhost:8000/create-room', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                roomname: roomNameCreate.value,
                password: passwordCreate.value,
            })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("create-message").textContent = data.response_message;
        })
        .catch(error => console.error('Error: ', error));
    });

    createButton.addEventListener("click", (event) => {
        roomNameCreate.value = "";
        passwordCreate.value = "";
    })

    // Deletes a room
    deleteButton.addEventListener("click", (event) => {
        event.preventDefault();

        fetch("http://localhost:8000/delete-room", {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                roomname: roomNameDelete.value,
                password: passwordDelete.value,
            })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById("delete-message").textContent = data.response_message;
        })
        .catch(error => console.error('Error: ', error));
    });

    deleteButton.addEventListener("click", (event) => {
        roomNameDelete.value = "";
        passwordDelete.value = "";
    })

    // Connection and chat
    connectButton.addEventListener("click", (event) => {
        event.preventDefault();

        const errorMessageDiv = document.getElementById("error-message");
        const p = document.createElement("p");

        if (roomNameJoin.value === "" || passwordJoin.value === "" || usernameJoin.value === "") {
            p.textContent = "Please fill in all fields!";
            errorMessageDiv.textContent = "";
            errorMessageDiv.append(p); 
            return;
        }

        fetch("http://localhost:8000/get_checks", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: usernameJoin.value,
                roomname: roomNameJoin.value,
                password: passwordJoin.value,
            })
        })
        .then(response => response.json())
        .then(data => {
            const checkResult = {
                bool: data.result,
                errorMessage: data.error_message
            };

            if (checkResult.bool === false) {
            p.textContent = checkResult.errorMessage;
            errorMessageDiv.textContent = "";
            errorMessageDiv.append(p); 
            return;
        }

        menuContainer.style.display = "none";

        const ws = new WebSocket(`ws://localhost:8000/ws`);

        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: "join",
                roomname: roomNameJoin.value,
                password: passwordJoin.value,
                username: usernameJoin.value
            }));

            const chatMessage = document.createElement("input");
            chatMessage.type = "text";
            chatMessage.placeholder = "Your message...";
            chatMessage.classList.add("chat-input");

            const sendMessageButton = document.createElement("button");
            sendMessageButton.type = "button";
            sendMessageButton.textContent = "Send";

            chatMessage.addEventListener("keydown", function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    sendMessageButton.click();
                }
            });

            const messageArea = document.getElementById("message-area");
            const inputArea = document.getElementById("input-area");

            inputArea.append(chatMessage, sendMessageButton);

            sendMessageButton.addEventListener("click", () => {
                ws.send(JSON.stringify({
                    type: "chat_message",
                    username: usernameJoin.value,
                    chat_message: chatMessage.value
                }));

                appendMessage(messageArea, "You", chatMessage.value);
                chatMessage.value = "";
            });

            ws.onmessage = (event) => {
                const eventData = JSON.parse(event.data);
                if (eventData.type === "join") {
                    const p = document.createElement("p");
                    const username = eventData.username;
                    p.textContent = `${username} entered the chat!`;
                    messageArea.append(p);
                } else if (eventData.type === "chat_message") {
                    const username = eventData.username;
                    const chatMessage = eventData.chat_message;
                    appendMessage(messageArea, username, chatMessage, eventData.timestamp);
                } else if (eventData.type === "leave") {
                    const p = document.createElement("p");
                    const username = eventData.username;
                    p.textContent = `${username} left the chat!`;
                    messageArea.append(p);
                } else if (eventData.type === "chat_history_type") {
                    const array = eventData.chat_history;
                    array.forEach(element => {
                        appendMessage(messageArea, element.username, element.chat_message, element.timestamp);
                    });
                }
            };
        };
        })
        .catch(error => console.error('Error: ', error));
    });
});
