import React from "react";
import { useState, useEffect } from "react";
import { useParams, useLocation } from "react-router-dom";


import ChessGame from "../Game/ChessGame";


const GamePage = () => {
    const { gameCode } = useParams(); 
    const location = useLocation(); 


    useEffect(() => {
        if (!gameCode) {
            console.error("No game code found");
            return;
        }
        console.log("Reconnecting to game:", gameCode);
    }, [gameCode]);

    return (
        <div className="widget page center-page">
            <div className="ChessGame">
                < ChessGame />
            </div>
        </div>
    );
};

export default GamePage;