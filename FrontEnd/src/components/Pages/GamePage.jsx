import React from "react";
import ChessGame from "../Game/ChessGame";

const GamePage = () => {
    return (
        <div className="widget page GamePage">
            <div className="ChessGame">
                < ChessGame />
            </div>
        </div>
    );
};

export default GamePage;