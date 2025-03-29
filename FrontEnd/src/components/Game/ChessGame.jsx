import { Canvas } from "@react-three/fiber";
import { CANVAS_HEIGHT, CANVAS_WIDTH } from "./constants";

import CameraControls from "./CameraControls";
import ChessBoard from "./ChessBoard";
// import Pieces from "./Pieces";

const ChessGame = () => {
    return (
        <Canvas
            camera={{ position: [0, 0, 0], fov: 50 }} 
            style={{ width: `${CANVAS_WIDTH}px`, height: `${CANVAS_HEIGHT}px` }}
        >
            <ambientLight intensity={0.1} />
            <CameraControls />
            <ChessBoard />
        </Canvas>
    );
};

export default ChessGame;
