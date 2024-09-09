import React from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import ChessBoard from "./ChessBoard";
import Pieces from "./Pieces";
import { CANVAS_HEIGHT, CANVAS_WIDTH } from "./constants";

const ChessGame = () => {
	return (
		<Canvas
			camera={{ position: [0, 10, 10], fov: 50 }}
			style={{ width: `${CANVAS_WIDTH}px`, height: `${CANVAS_HEIGHT}px` }}
		>
			{/* Ambient light and directional light */}
			<ambientLight intensity={0.5} />
			<directionalLight position={[10, 10, 5]} intensity={1} />

			{/* Orbit Controls for camera movement */}
			<OrbitControls />

			{/* Chess Board and Pieces */}
			<ChessBoard />
			<Pieces />
		</Canvas>
	);
};

export default ChessGame;