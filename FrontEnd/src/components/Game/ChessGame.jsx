import { Canvas } from "@react-three/fiber";
import { CANVAS_HEIGHT, CANVAS_WIDTH } from "./constants";

import CameraControls from "./CameraControls";
import ChessBoard from "./ChessBoard";

const ChessGame = ({
    gameId,
    gameType,
    boardSize,
    state,
    setStates,
    turn,
    setTurn,
    players,
    setHistory
}) => {
    return (
        <Canvas
            camera={{ position: [0, 0, 0], fov: 50 }}
            style={{ width: `${CANVAS_WIDTH}px`, height: `${CANVAS_HEIGHT}px` }}
        >
            <ambientLight intensity={0.1} />
            <CameraControls />
            <ChessBoard
                gameId={gameId}
                gameType={gameType}
                boardSize={boardSize}
                state={state}
                setStates={setStates}
                turn={turn}
                setTurn={setTurn}
                players={players}
                setHistory={setHistory}
            />
        </Canvas>
    );
};

export default ChessGame;
