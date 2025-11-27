'use strict';

window.addEventListener("DOMContentLoaded", () => {
    const menuContainer = document.getElementById("menu-container-id");
    const chatHeader = document.getElementById("chat-header");
    const backButton = document.getElementById("back-button");
    const roomTitle = document.getElementById("room-title");
    const activeUserList = document.getElementById("active-user-list");

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

    let currentWebSocket = null;
    let currentUsername = null;
    let activeUsers = [];

    function appendMessage(messageArea, username, chatMessage, timestamp) {
        const date = timestamp ? new Date(timestamp) : new Date();
        const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const p = document.createElement("p");
        const isSelf = username === "You" || username === currentUsername;
        p.classList.add("chat-message");
        p.classList.add(isSelf ? "self" : "other");
        p.textContent = `${timeString} ${username}: ${chatMessage}`;
        const wrapper = document.createElement("div");
        wrapper.classList.add("message-row", isSelf ? "self" : "other");
        wrapper.append(p);
        messageArea.append(wrapper);
    }

    function appendSystemMessage(messageArea, text) {
        const p = document.createElement("p");
        p.textContent = text;
        const wrapper = document.createElement("div");
        wrapper.classList.add("message-row", "system");
        p.classList.add("system-message");
        wrapper.append(p);
        messageArea.append(wrapper);
    }

    function saveSession(roomname, password, username) {
        sessionStorage.setItem('chatSession', JSON.stringify({
            roomname,
            password,
            username
        }));
    }

    function getSession() {
        const session = sessionStorage.getItem('chatSession');
        return session ? JSON.parse(session) : null;
    }

    function clearSession() {
        sessionStorage.removeItem('chatSession');
    }

    function renderActiveUsers() {
        if (!activeUserList) return;
        activeUserList.textContent = activeUsers.length ? activeUsers.join(", ") : "Keine Nutzer";
    }

    function showMenu() {
        menuContainer.style.display = "flex";
        chatHeader.style.display = "none";
        currentUsername = null;
        activeUsers = [];
        renderActiveUsers();
        document.getElementById("message-area").innerHTML = "";
        document.getElementById("input-area").innerHTML = "";
    }

    function showChat(roomname) {
        menuContainer.style.display = "none";
        chatHeader.style.display = "flex";
        roomTitle.textContent = `Room: ${roomname}`;
    }

    function connectToRoom(roomname, password, username) {
        const ws = new WebSocket(`ws://localhost:8000/ws`);
        currentWebSocket = ws;
        currentUsername = username;

        ws.onopen = () => {
            ws.send(JSON.stringify({
                type: "join",
                roomname: roomname,
                password: password,
                username: username
            }));

            showChat(roomname);

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
                if (chatMessage.value.trim() === "") return;
                ws.send(JSON.stringify({
                    type: "chat_message",
                    username: username,
                    chat_message: chatMessage.value
                }));

                appendMessage(messageArea, "You", chatMessage.value);
                chatMessage.value = "";
            });

            ws.onmessage = (event) => {
                const eventData = JSON.parse(event.data);
                if (eventData.type === "join") {
                    const joinedUsername = eventData.username;
                    appendSystemMessage(messageArea, `${joinedUsername} entered the chat!`);
                } else if (eventData.type === "chat_message") {
                    const msgUsername = eventData.username;
                    const msgContent = eventData.chat_message;
                    appendMessage(messageArea, msgUsername, msgContent, eventData.timestamp);
                } else if (eventData.type === "leave") {
                    const leftUsername = eventData.username;
                    appendSystemMessage(messageArea, `${leftUsername} left the chat!`);
                } else if (eventData.type === "chat_history_type") {
                    const array = eventData.chat_history;
                    array.forEach(element => {
                        if (element.chat_message === "entered the chat!" || element.chat_message === "left the chat!") {
                            appendSystemMessage(messageArea, `${element.username} ${element.chat_message}`);
                        } else {
                            appendMessage(messageArea, element.username, element.chat_message, element.timestamp);
                        }
                    });
                } else if (eventData.type === "active_users") {
                    activeUsers = eventData.users || [];
                    renderActiveUsers();
                }
            };

            ws.onclose = () => {
                currentWebSocket = null;
            };
        };

        ws.onerror = () => {
            clearSession();
            showMenu();
        };
    }

    // Back button handler
    backButton.addEventListener("click", () => {
        if (currentWebSocket) {
            currentWebSocket.close();
            currentWebSocket = null;
        }
        clearSession();
        showMenu();
    });

    // Check for existing session on page load
    const existingSession = getSession();
    if (existingSession) {
        // Verify the session is still valid
        fetch("http://localhost:8000/get_checks", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: existingSession.username,
                roomname: existingSession.roomname,
                password: existingSession.password,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.result === true || data.error_message === "Your entered username is already taken by someone else!") {
                // Session valid, reconnect
                connectToRoom(existingSession.roomname, existingSession.password, existingSession.username);
            } else {
                // Session invalid, clear and show menu
                clearSession();
                showMenu();
            }
        })
        .catch(() => {
            clearSession();
            showMenu();
        });
    } else {
        showMenu();
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

        roomNameCreate.value = "";
        passwordCreate.value = "";
    });

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

        roomNameDelete.value = "";
        passwordDelete.value = "";
    });

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

            // Save session before connecting
            saveSession(roomNameJoin.value, passwordJoin.value, usernameJoin.value);
            connectToRoom(roomNameJoin.value, passwordJoin.value, usernameJoin.value);
        })
        .catch(error => console.error('Error: ', error));
    });
});
