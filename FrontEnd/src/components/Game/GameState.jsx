import create from "zustand";

const useGameStore = create((set) => ({
  turn: "white",
  boardState: [], // Add initial board state
  selectPiece: (pieceId) => set((state) => ({ ...state, selectedPiece: pieceId })),
  movePiece: (from, to) =>
    set((state) => {
      // Handle piece movement logic
    }),
  // Add more state and actions as needed
}));

export default useGameStore;