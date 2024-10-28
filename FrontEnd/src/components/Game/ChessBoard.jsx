import React from "react";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";

const ChessBoard = () => {
  // Generate 8x8 board
  const board = [];
  for (let i = 0; i < 8; i++) {
    for (let j = 0; j < 8; j++) {
      const isBlack = (i + j) % 2 === 1; // Alternate colors
      board.push(
        <mesh
          key={`${i}-${j}`}
          position={[i - 3.5, 0, j - 3.5]} // Position each tile
          onClick={() => handleTileClick(i, j)} // Handle tile click
        >
          <boxGeometry args={[1, 0.2, 1]} />
          <meshStandardMaterial color={isBlack ? "black" : "white"} />
        </mesh>
      );
    }
  }

  const handleTileClick = (i, j) => {
    console.log(`Clicked on tile: ${i}, ${j}`);
    // Handle tile selection logic
  };

  return <group>{board}</group>;
};

export default ChessBoard;