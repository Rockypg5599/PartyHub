import React from "react";
import RoomCreate from "./components/lobby/RoomCreate";
import PlayerList from "./components/lobby/PlayerList";

export default function App() {
  return (
    <div>
      <h1>Room Game</h1>
      <RoomCreate />
      <PlayerList />
    </div>
  );
}
