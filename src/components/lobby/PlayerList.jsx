import React from "react";
import { useRoomStore } from "../../state/roomStore";

export default function PlayerList() {
  const players = useRoomStore((s) => s.players);

  return (
    <div>
      <h3>Players</h3>
      {players.map((p, i) => (
        <div key={i}>{p.name}</div>
      ))}
    </div>
  );
}
