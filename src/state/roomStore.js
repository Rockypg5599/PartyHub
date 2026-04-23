import { create } from "zustand";

export const useRoomStore = create((set) => ({
  roomId: null,
  hostId: null,
  players: [],

  setRoom: (roomId, hostId) => set({ roomId, hostId }),
  setPlayers: (players) => set({ players }),
}));
