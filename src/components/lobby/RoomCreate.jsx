import React from "react";
import { socket } from "../../core/socket";

export default function RoomCreate() {
  const createRoom = () => {
    socket.emit("room:create", { name: "test" });
  };

  return <button onClick={createRoom}>Create Room</button>;
}
