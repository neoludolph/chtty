'use strict';

// DOM-Initialisierung
window.addEventListener("DOMContentLoaded", () => {
    // UI-Elemente
    const menuContainer = document.getElementById("menu-container-id");
    const chatHeader = document.getElementById("chat-header");
    const backButton = document.getElementById("back-button");
    const roomTitle = document.getElementById("room-title");
    const activeUserList = document.getElementById("active-user-list");

    // Eingabefelder für Raumnamen
    const roomNameCreate = document.getElementById("room-name-create");
    const roomNameJoin = document.getElementById("room-name-join");
    const roomNameDelete = document.getElementById("room-name-delete");

    // Eingabefelder für Passwörter
    const passwordCreate = document.getElementById("password-create");
    const passwordJoin = document.getElementById("password-join");
    const passwordDelete = document.getElementById("password-delete");

    const usernameJoin = document.getElementById("username-join");

    // Action-Buttons
    const createButton = document.getElementById("create-button");
    const connectButton = document.getElementById("connect-button");
    const deleteButton = document.getElementById("delete-button");

    // Zustandsvariablen
    let currentWebSocket = null;
    let currentUsername = null;
    let activeUsers = [];

    // Hilfsfunktionen für Chat-Nachrichten
    function appendMessage(messageArea, username, chatMessage, timestamp) {
        const date = timestamp ? new Date(timestamp) : new Date();
        const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const isSelf = username === "You" || username === currentUsername;

        // Nachrichtenblase erstellen
        const messageBubble = document.createElement("div");
        messageBubble.classList.add("chat-message", isSelf ? "self" : "other");

        const messageText = document.createElement("p");
        messageText.classList.add("message-text");
        messageText.textContent = `${username}: ${chatMessage}`;

        const timestampElement = document.createElement("span");
        timestampElement.classList.add("message-timestamp");
        timestampElement.textContent = timeString;

        messageBubble.append(messageText, timestampElement);

        // Wrapper für Ausrichtung
        const wrapper = document.createElement("div");
        wrapper.classList.add("message-row", isSelf ? "self" : "other");
        wrapper.append(messageBubble);
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

    // Session-Management
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

    // UI-Update-Funktionen
    function updateFormMessage(elementId, message, type = "error") {
        const element = document.getElementById(elementId);
        if (!element) return;
        element.textContent = message || "";
        element.classList.remove("success", "error");
        if (!message) return;
        element.classList.add(type === "success" ? "success" : "error");
    }

    function renderActiveUsers() {
        if (!activeUserList) return;
        activeUserList.textContent = activeUsers.length ? activeUsers.join(", ") : "Keine Nutzer";
    }

    // Ansichtsfunktionen
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
    // WebSocket-Verbindung
    function connectToRoom(roomname, password, username) {
        const ws = new WebSocket(`ws://localhost:8000/ws`);
        currentWebSocket = ws;
        currentUsername = username;

        ws.onopen = () => {
            // Beitrittsdaten senden
            ws.send(JSON.stringify({
                type: "join",
                roomname: roomname,
                password: password,
                username: username
            }));

            showChat(roomname);

            // Chat-Eingabe erstellen
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

            // Nachricht senden
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

            // Nachrichten empfangen und verarbeiten
            ws.onmessage = (event) => {
                const eventData = JSON.parse(event.data);

                if (eventData.type === "join") {
                    const joinedUsername = eventData.username;
                    if (joinedUsername !== currentUsername) {
                        appendSystemMessage(messageArea, `${joinedUsername} entered the chat!`);
                    }
                } else if (eventData.type === "chat_message") {
                    const msgUsername = eventData.username;
                    const msgContent = eventData.chat_message;
                    appendMessage(messageArea, msgUsername, msgContent, eventData.timestamp);
                } else if (eventData.type === "leave") {
                    const leftUsername = eventData.username;
                    if (leftUsername !== currentUsername) {
                        appendSystemMessage(messageArea, `${leftUsername} left the chat!`);
                    }
                } else if (eventData.type === "chat_history_type") {
                    const array = eventData.chat_history;
                    array.forEach(element => {
                        if (element.chat_message === "entered the chat!" || element.chat_message === "left the chat!") {
                            if (element.username !== currentUsername) {
                                appendSystemMessage(messageArea, `${element.username} ${element.chat_message}`);
                            }
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

    // Zurück-Button Event-Listener
    backButton.addEventListener("click", () => {
        if (currentWebSocket) {
            currentWebSocket.close();
            currentWebSocket = null;
        }
        clearSession();
        showMenu();
    });

    // API-Response-Handler
    function handleJsonResponse(response) {
        if (response.ok) {
            return response.json();
        }
        return response.json()
            .catch(() => ({}))
            .then(data => {
                const message = data?.detail || data?.response_message || "Something went wrong.";
                throw new Error(message);
            });
    }

    // Session-Wiederherstellung beim Laden
    const existingSession = getSession();
    if (existingSession) {
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
            .then(handleJsonResponse)
            .then(data => {
                if (data.result === true || data.error_message === "Your entered username is already taken by someone else!") {
                    connectToRoom(existingSession.roomname, existingSession.password, existingSession.username);
                } else {
                    clearSession();
                    showMenu();
                }
            })
            .catch((error) => {
                updateFormMessage("error-message", error.message, "error");
                clearSession();
                showMenu();
            });
    } else {
        showMenu();
    }

    // Enter-Taste Event-Listener
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

    // Raum erstellen
    createButton.addEventListener("click", (event) => {
        event.preventDefault();

        if (roomNameCreate.value === "" || passwordCreate.value === "") {
            updateFormMessage("create-message", "Please fill in all fields!", "error");
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
            .then(handleJsonResponse)
            .then(data => {
                const responseText = data.response_message || "Unknown response.";
                const type = responseText.toLowerCase().includes("success") ? "success" : "error";
                updateFormMessage("create-message", responseText, type);
            })
            .catch((error) => {
                updateFormMessage("create-message", error.message || "Something went wrong. Please try again.", "error");
            });

        roomNameCreate.value = "";
        passwordCreate.value = "";
    });

    // Raum löschen
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
            .then(handleJsonResponse)
            .then(data => {
                const responseText = data.response_message || "Unknown response.";
                const type = responseText.toLowerCase().includes("success") ? "success" : "error";
                updateFormMessage("delete-message", responseText, type);
            })
            .catch((error) => {
                updateFormMessage("delete-message", error.message || "Something went wrong. Please try again.", "error");
            });

        roomNameDelete.value = "";
        passwordDelete.value = "";
    });

    // Raum beitreten
    connectButton.addEventListener("click", (event) => {
        event.preventDefault();

        if (roomNameJoin.value === "" || passwordJoin.value === "" || usernameJoin.value === "") {
            updateFormMessage("error-message", "Please fill in all fields!", "error");
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
            .then(handleJsonResponse)
            .then(data => {
                const checkResult = {
                    bool: data.result,
                    errorMessage: data.error_message
                };

                if (checkResult.bool === false) {
                    updateFormMessage("error-message", checkResult.errorMessage || "Something went wrong.", "error");
                    return;
                }

                updateFormMessage("error-message", "");
                saveSession(roomNameJoin.value, passwordJoin.value, usernameJoin.value);
                connectToRoom(roomNameJoin.value, passwordJoin.value, usernameJoin.value);
            })
            .catch((error) => {
                updateFormMessage("error-message", error.message || "Could not connect. Please try again.", "error");
            });
    });
});
