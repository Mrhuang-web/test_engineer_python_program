const ws = new WebSocket("ws://localhost:8888/ws");

ws.onmessage = function (event) {
    const data = JSON.parse(event.data);
    if (data.type === "status") {
        document.getElementById("status").innerText = JSON.stringify(data.data, null, 2);
    } else if (data.type === "logs") {
        document.getElementById("logs").innerText = data.data.join("\n");
    } else if (data.type === "error") {
        alert(data.message);
    }
};

function getServerStatus() {
    ws.send(JSON.stringify({ type: "get_status" }));
}

function getLogs() {
    ws.send(JSON.stringify({ type: "get_logs" }));
}