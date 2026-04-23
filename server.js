
const express = require("express");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static("public"));

let rooms = {};

function generateCode() {
  return Math.random().toString(36).substring(2, 7).toUpperCase();
}

io.on("connection", (socket) => {
  console.log("User connected");

  socket.on("createRoom", (username) => {
    const code = generateCode();
    rooms[code] = { users: [] };
    socket.join(code);
    rooms[code].users.push({ id: socket.id, username });
    socket.emit("roomCreated", code);
  });

  socket.on("joinRoom", ({ code, username }) => {
    if (rooms[code]) {
      socket.join(code);
      rooms[code].users.push({ id: socket.id, username });
      io.to(code).emit("chat", username + " joined the room");
    } else {
      socket.emit("errorMsg", "Room not found");
    }
  });

  socket.on("chat", ({ code, message, username }) => {
    io.to(code).emit("chat", username + ": " + message);
  });

  socket.on("disconnect", () => {
    console.log("User disconnected");
  });
});

server.listen(3000, () => console.log("Server running on http://localhost:3000"));
