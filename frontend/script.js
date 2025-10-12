window.addEventListener("DOMContentLoaded", () => {
        /** @type {HTMLInputElement} */
    const input = document.getElementById("input");
    const button = document.getElementById("btn");
    const messagesDiv = document.getElementById("messages");

    const userId = 1;
    const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);

    const ul = document.createElement("ul");
    messagesDiv.append(ul);

    button.addEventListener("click", () => {
        const value = input.value;
        ws.send(value);
        const li = document.createElement("li");
        li.textContent = value;
        ul.append(li);
        value = "";
    });
});