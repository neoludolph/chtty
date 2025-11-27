// Aktiviert den strikten Modus für sichereren Code
'use strict';

// Wartet, bis das DOM vollständig geladen ist
window.addEventListener("DOMContentLoaded", () => {
    // Holt das Menü-Container-Element
    const menuContainer = document.getElementById("menu-container-id");
    // Holt das Chat-Header-Element
    const chatHeader = document.getElementById("chat-header");
    // Holt den Zurück-Button
    const backButton = document.getElementById("back-button");
    // Holt das Element für den Raumtitel
    const roomTitle = document.getElementById("room-title");
    // Holt das Element für die Liste der aktiven Benutzer
    const activeUserList = document.getElementById("active-user-list");

    // Holt das Eingabefeld für den Raumnamen beim Erstellen
    const roomNameCreate = document.getElementById("room-name-create");
    // Holt das Eingabefeld für den Raumnamen beim Beitreten
    const roomNameJoin = document.getElementById("room-name-join");
    // Holt das Eingabefeld für den Raumnamen beim Löschen
    const roomNameDelete = document.getElementById("room-name-delete");

    // Holt das Eingabefeld für das Passwort beim Erstellen
    const passwordCreate = document.getElementById("password-create");
    // Holt das Eingabefeld für das Passwort beim Beitreten
    const passwordJoin = document.getElementById("password-join");
    // Holt das Eingabefeld für das Passwort beim Löschen
    const passwordDelete = document.getElementById("password-delete");

    // Holt das Eingabefeld für den Benutzernamen beim Beitreten
    const usernameJoin = document.getElementById("username-join");

    // Holt den Button zum Erstellen eines Raums
    const createButton = document.getElementById("create-button");
    // Holt den Button zum Verbinden mit einem Raum
    const connectButton = document.getElementById("connect-button");
    // Holt den Button zum Löschen eines Raums
    const deleteButton = document.getElementById("delete-button");

    // Speichert die aktuelle WebSocket-Verbindung
    let currentWebSocket = null;
    // Speichert den aktuellen Benutzernamen
    let currentUsername = null;
    // Speichert die Liste der aktiven Benutzer
    let activeUsers = [];

    // Fügt eine Nachricht zum Chat-Bereich hinzu
    function appendMessage(messageArea, username, chatMessage, timestamp) {
        // Erstellt ein Datumsobjekt aus dem Zeitstempel oder der aktuellen Zeit
        const date = timestamp ? new Date(timestamp) : new Date();
        // Formatiert die Zeit als String
        const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        // Prüft, ob die Nachricht vom eigenen Benutzer stammt
        const isSelf = username === "You" || username === currentUsername;

        // Erstellt das Element für die Nachrichtenblase
        const messageBubble = document.createElement("div");
        // Fügt Klassen für Styling hinzu
        messageBubble.classList.add("chat-message", isSelf ? "self" : "other");

        // Erstellt das Element für den Nachrichtentext
        const messageText = document.createElement("p");
        // Fügt Klasse für Styling hinzu
        messageText.classList.add("message-text");
        // Setzt den Textinhalt
        messageText.textContent = `${username}: ${chatMessage}`;

        // Erstellt das Element für den Zeitstempel
        const timestampElement = document.createElement("span");
        // Fügt Klasse für Styling hinzu
        timestampElement.classList.add("message-timestamp");
        // Setzt den Zeitstempel-Text
        timestampElement.textContent = timeString;

        // Fügt Text und Zeitstempel zur Blase hinzu
        messageBubble.append(messageText, timestampElement);

        // Erstellt einen Wrapper für die Ausrichtung
        const wrapper = document.createElement("div");
        // Fügt Klassen für Ausrichtung hinzu
        wrapper.classList.add("message-row", isSelf ? "self" : "other");
        // Fügt die Blase zum Wrapper hinzu
        wrapper.append(messageBubble);
        // Fügt den Wrapper zum Nachrichtenbereich hinzu
        messageArea.append(wrapper);
    }

    // Fügt eine Systemnachricht zum Chat-Bereich hinzu
    function appendSystemMessage(messageArea, text) {
        // Erstellt das Absatzelement
        const p = document.createElement("p");
        // Setzt den Textinhalt
        p.textContent = text;
        // Erstellt einen Wrapper
        const wrapper = document.createElement("div");
        // Fügt Klassen für Systemnachrichten hinzu
        wrapper.classList.add("message-row", "system");
        // Fügt Klasse für Styling hinzu
        p.classList.add("system-message");
        // Fügt den Absatz zum Wrapper hinzu
        wrapper.append(p);
        // Fügt den Wrapper zum Nachrichtenbereich hinzu
        messageArea.append(wrapper);
    }

    // Speichert die Sitzungsdaten im SessionStorage
    function saveSession(roomname, password, username) {
        // Setzt das Item im SessionStorage
        sessionStorage.setItem('chatSession', JSON.stringify({
            roomname,
            password,
            username
        }));
    }

    // Ruft die Sitzungsdaten aus dem SessionStorage ab
    function getSession() {
        // Holt das Item aus dem SessionStorage
        const session = sessionStorage.getItem('chatSession');
        // Parst das JSON oder gibt null zurück
        return session ? JSON.parse(session) : null;
    }

    // Löscht die Sitzungsdaten aus dem SessionStorage
    function clearSession() {
        // Entfernt das Item
        sessionStorage.removeItem('chatSession');
    }

    // Aktualisiert die Formularnachricht
    function updateFormMessage(elementId, message, type = "error") {
        // Holt das Nachrichtenelement
        const element = document.getElementById(elementId);
        // Bricht ab, wenn das Element nicht existiert
        if (!element) return;
        // Setzt den Textinhalt
        element.textContent = message || "";
        // Entfernt alte Klassen
        element.classList.remove("success", "error");
        // Bricht ab, wenn keine Nachricht vorhanden ist
        if (!message) return;
        // Fügt die entsprechende Klasse hinzu
        element.classList.add(type === "success" ? "success" : "error");
    }

    // Rendert die Liste der aktiven Benutzer
    function renderActiveUsers() {
        // Bricht ab, wenn das Element nicht existiert
        if (!activeUserList) return;
        // Setzt den Textinhalt basierend auf der Liste
        activeUserList.textContent = activeUsers.length ? activeUsers.join(", ") : "Keine Nutzer";
    }

    // Zeigt das Hauptmenü an
    function showMenu() {
        // Zeigt den Menü-Container
        menuContainer.style.display = "flex";
        // Versteckt den Chat-Header
        chatHeader.style.display = "none";
        // Setzt den aktuellen Benutzernamen zurück
        currentUsername = null;
        // Leert die Liste der aktiven Benutzer
        activeUsers = [];
        // Aktualisiert die Anzeige der aktiven Benutzer
        renderActiveUsers();
        // Leert den Nachrichtenbereich
        document.getElementById("message-area").innerHTML = "";
        // Leert den Eingabebereich
        document.getElementById("input-area").innerHTML = "";
    }

    // Zeigt den Chat-Bereich an
    function showChat(roomname) {
        // Versteckt den Menü-Container
        menuContainer.style.display = "none";
        // Zeigt den Chat-Header
        chatHeader.style.display = "flex";
        // Setzt den Raumtitel
        roomTitle.textContent = `Room: ${roomname}`;
    }

    // Verbindet mit einem Chat-Raum
    function connectToRoom(roomname, password, username) {
        // Erstellt eine neue WebSocket-Verbindung
        const ws = new WebSocket(`ws://localhost:8000/ws`);
        // Speichert die WebSocket-Referenz
        currentWebSocket = ws;
        // Speichert den Benutzernamen
        currentUsername = username;

        // Wird aufgerufen, wenn die Verbindung geöffnet wird
        ws.onopen = () => {
            // Sendet die Beitrittsdaten
            ws.send(JSON.stringify({
                type: "join",
                roomname: roomname,
                password: password,
                username: username
            }));

            // Zeigt die Chat-Oberfläche an
            showChat(roomname);

            // Erstellt das Eingabefeld für Nachrichten
            const chatMessage = document.createElement("input");
            chatMessage.type = "text";
            chatMessage.placeholder = "Your message...";
            chatMessage.classList.add("chat-input");

            // Erstellt den Senden-Button
            const sendMessageButton = document.createElement("button");
            sendMessageButton.type = "button";
            sendMessageButton.textContent = "Send";

            // Fügt Event-Listener für Enter-Taste hinzu
            chatMessage.addEventListener("keydown", function (event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    sendMessageButton.click();
                }
            });

            // Holt die Bereiche für Nachrichten und Eingabe
            const messageArea = document.getElementById("message-area");
            const inputArea = document.getElementById("input-area");

            // Fügt Eingabefeld und Button zum Eingabebereich hinzu
            inputArea.append(chatMessage, sendMessageButton);

            // Fügt Event-Listener für Klick auf Senden hinzu
            sendMessageButton.addEventListener("click", () => {
                // Prüft auf leere Eingabe
                if (chatMessage.value.trim() === "") return;
                // Sendet die Nachricht über WebSocket
                ws.send(JSON.stringify({
                    type: "chat_message",
                    username: username,
                    chat_message: chatMessage.value
                }));

                // Fügt die eigene Nachricht lokal hinzu
                appendMessage(messageArea, "You", chatMessage.value);
                // Leert das Eingabefeld
                chatMessage.value = "";
            });

            // Wird aufgerufen, wenn eine Nachricht empfangen wird
            ws.onmessage = (event) => {
                // Parst die empfangenen Daten
                const eventData = JSON.parse(event.data);
                // Behandelt Beitrittsnachrichten
                if (eventData.type === "join") {
                    const joinedUsername = eventData.username;
                    if (joinedUsername !== currentUsername) {
                        appendSystemMessage(messageArea, `${joinedUsername} entered the chat!`);
                    }
                // Behandelt Chat-Nachrichten
                } else if (eventData.type === "chat_message") {
                    const msgUsername = eventData.username;
                    const msgContent = eventData.chat_message;
                    appendMessage(messageArea, msgUsername, msgContent, eventData.timestamp);
                // Behandelt Verlassensnachrichten
                } else if (eventData.type === "leave") {
                    const leftUsername = eventData.username;
                    if (leftUsername !== currentUsername) {
                        appendSystemMessage(messageArea, `${leftUsername} left the chat!`);
                    }
                // Behandelt Chat-Verlauf
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
                // Behandelt Liste aktiver Benutzer
                } else if (eventData.type === "active_users") {
                    activeUsers = eventData.users || [];
                    renderActiveUsers();
                }
            };

            // Wird aufgerufen, wenn die Verbindung geschlossen wird
            ws.onclose = () => {
                currentWebSocket = null;
            };
        };

        // Wird aufgerufen, wenn ein Fehler auftritt
        ws.onerror = () => {
            clearSession();
            showMenu();
        };
    }

    // Event-Listener für den Zurück-Button
    backButton.addEventListener("click", () => {
        // Schließt die WebSocket-Verbindung, falls vorhanden
        if (currentWebSocket) {
            currentWebSocket.close();
            currentWebSocket = null;
        }
        // Löscht die Sitzung
        clearSession();
        // Zeigt das Menü an
        showMenu();
    });

    // Hilfsfunktion zur Verarbeitung von JSON-Antworten
    function handleJsonResponse(response) {
        // Wenn die Antwort OK ist, gib JSON zurück
        if (response.ok) {
            return response.json();
        }
        // Andernfalls versuche Fehlerdetails zu lesen und wirf Fehler
        return response.json()
            .catch(() => ({}))
            .then(data => {
                const message = data?.detail || data?.response_message || "Something went wrong.";
                throw new Error(message);
            });
    }

    // Prüft auf existierende Sitzung beim Laden der Seite
    const existingSession = getSession();
    if (existingSession) {
        // Überprüft, ob die Sitzung noch gültig ist
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
            // Wenn gültig oder nur Benutzername vergeben (was bei Reconnect ok sein kann, aber hier Logik etwas unscharf)
            if (data.result === true || data.error_message === "Your entered username is already taken by someone else!") {
                // Sitzung gültig, wieder verbinden
                connectToRoom(existingSession.roomname, existingSession.password, existingSession.username);
            } else {
                // Sitzung ungültig, löschen und Menü zeigen
                clearSession();
                showMenu();
            }
        })
        .catch((error) => {
            // Bei Fehler Nachricht anzeigen und Menü zeigen
            updateFormMessage("error-message", error.message, "error");
            clearSession();
            showMenu();
        });
    } else {
        // Keine Sitzung, Menü zeigen
        showMenu();
    }

    // Event-Listener für Enter-Taste im Passwort-Feld (Erstellen)
    passwordCreate.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            createButton.click();
        }
    });

    // Event-Listener für Enter-Taste im Benutzernamen-Feld (Beitreten)
    usernameJoin.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            connectButton.click();
        }
    });

    // Event-Listener für Enter-Taste im Passwort-Feld (Löschen)
    passwordDelete.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            deleteButton.click();
        }
    });

    // Event-Listener für Klick auf Erstellen-Button
    createButton.addEventListener("click", (event) => {
        event.preventDefault();

        // Validiert Eingabefelder
        if (roomNameCreate.value === "" || passwordCreate.value === "") {
            updateFormMessage("create-message", "Please fill in all fields!", "error");
            return;
        }

        // Sendet Anfrage zum Erstellen des Raums
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
            // Zeigt Erfolgs- oder Fehlermeldung an
            const responseText = data.response_message || "Unknown response.";
            const type = responseText.toLowerCase().includes("success") ? "success" : "error";
            updateFormMessage("create-message", responseText, type);
        })
        .catch((error) => {
            // Zeigt Fehlermeldung an
            updateFormMessage("create-message", error.message || "Something went wrong. Please try again.", "error");
        });

        // Leert die Eingabefelder
        roomNameCreate.value = "";
        passwordCreate.value = "";
    });

    // Event-Listener für Klick auf Löschen-Button
    deleteButton.addEventListener("click", (event) => {
        event.preventDefault();

        // Sendet Anfrage zum Löschen des Raums
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
            // Zeigt Erfolgs- oder Fehlermeldung an
            const responseText = data.response_message || "Unknown response.";
            const type = responseText.toLowerCase().includes("success") ? "success" : "error";
            updateFormMessage("delete-message", responseText, type);
        })
        .catch((error) => {
            // Zeigt Fehlermeldung an
            updateFormMessage("delete-message", error.message || "Something went wrong. Please try again.", "error");
        });

        // Leert die Eingabefelder
        roomNameDelete.value = "";
        passwordDelete.value = "";
    });

    // Event-Listener für Klick auf Verbinden-Button
    connectButton.addEventListener("click", (event) => {
        event.preventDefault();

        // Validiert Eingabefelder
        if (roomNameJoin.value === "" || passwordJoin.value === "" || usernameJoin.value === "") {
            updateFormMessage("error-message", "Please fill in all fields!", "error");
            return;
        }

        // Überprüft die Zugangsdaten
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

            // Wenn Prüfung fehlschlägt, Fehler anzeigen
            if (checkResult.bool === false) {
                updateFormMessage("error-message", checkResult.errorMessage || "Something went wrong.", "error");
                return;
            }

            // Fehlermeldung löschen
            updateFormMessage("error-message", "");

            // Sitzung speichern und verbinden
            saveSession(roomNameJoin.value, passwordJoin.value, usernameJoin.value);
            connectToRoom(roomNameJoin.value, passwordJoin.value, usernameJoin.value);
        })
        .catch((error) => {
            // Zeigt Fehlermeldung an
            updateFormMessage("error-message", error.message || "Could not connect. Please try again.", "error");
        });
    });
});
