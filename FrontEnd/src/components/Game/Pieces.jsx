import React, { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { useSpring, animated } from "@react-spring/three";

const Piece = ({ type, position, onClick }) => {
  const ref = useRef();

  // Example animation for moving pieces
  const { position: animatedPosition } = useSpring({
    position: position, // Move to new position
    config: { mass: 1, tension: 180, friction: 12 },
  });

  return (
    <animated.mesh
      ref={ref}
      position={animatedPosition}
      onClick={onClick}
      castShadow
    >
      <boxGeometry args={[0.8, 0.8, 0.8]} />
      <meshStandardMaterial color="red" />
    </animated.mesh>
  );
};

const Pieces = () => {
  // Example: Map over pieces data
  const pieces = [
    { type: "pawn", position: [0, 0.5, 0], id: 1 },
    { type: "knight", position: [1, 0.5, 0], id: 2 },
    // Add more pieces as needed
  ];

  return (
    <group>
      {pieces.map((piece) => (
        <Piece
          key={piece.id}
          type={piece.type}
          position={piece.position}
          onClick={() => console.log("Clicked piece", piece.type)}
        />
      ))}
    </group>
  );
};

export default Pieces;