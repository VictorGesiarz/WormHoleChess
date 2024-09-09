import React from "react";
import ChessGame from "../Game/ChessGame";
import "./MainPage.css";

const MainPage = () => {
    return (
        <div className="MainPage">
            <h1>WormHoleChess</h1>

            <div className="ChessGame">
                < ChessGame />
            </div>
        </div>
    );
};

export default MainPage;