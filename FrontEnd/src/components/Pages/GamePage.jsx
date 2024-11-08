import React from "react";
import ChessGame from "../Game/ChessGame";
import "./MainPage.css";

const GamePage = () => {
    return (
        <div className="GamePage">
            <h1>WormHoleChess</h1>

            <div className="ChessGame">
                < ChessGame />
            </div>
        </div>
    );
};

export default GamePage;