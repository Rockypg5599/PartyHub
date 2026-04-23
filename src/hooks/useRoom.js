import { useEffect } from "react";
import { useRoomStore } from "../state/roomStore";
import { socket } from "../core/socket";

export function useRoom() {
  const setPlayers = useRoomStore((s) => s.setPlayers);

  useEffect(() => {
    socket.on("room:update", setPlayers);
  }, []);
}
