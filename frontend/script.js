window.addEventListener("DOMContentLoaded", () => {
        /** @type {HTMLInputElement} */
    const input = document.getElementById("input");
    const button = document.getElementById("btn");
    const messagesDiv = document.getElementById("messages");

    const userId = 1;
    const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);

    const div = document.createElement("div");
    messagesDiv.append(div);

    button.addEventListener("click", () => {
        ws.send(input.value);
        const p = document.createElement("p");
        p.textContent = `You: ${input.value}`;
        div.append(p);
        input.value = "";
    });
});