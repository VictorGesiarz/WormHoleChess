import React from "react";
import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { useWebSocket } from "../../utils/WebSocketProvider";
// import "./GamePage.css"; 


import ChessGame from "../Game/ChessGame";


const GamePage = () => {
    const { gameCode } = useParams(); 
    const { socket } = useWebSocket(); 

    const [thisPlayer, setThisPlayer] = useState(null); 
    const [otherPlayers, setOtherPlayers] = useState([]);
    const [currentTurn, setCurrentTurn] = useState(null);

    const [moves, setMoves] = useState([]);

    useEffect(() => {
        if (!gameCode) {
            console.error("Wrong game code!");
            return; 
        }

        if (!socket) {
            console.error("WebSocket connection missing!");
            return;
        }

        const handleSocketMessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === "game_start") {
                setThisPlayer(data.thisPlayer);
                setOtherPlayers(data.otherPlayers); 
                setMoves(data.moves);
                setCurrentTurn(data.current_turn);
            } 
            else if (data.type === "move_made") {
                setMoves((prevMoves) => [...prevMoves, data.move]);
                setCurrentTurn(data.next_turn);
            }
        };

        socket.addEventListener("message", handleSocketMessage);

        return () => {
            socket.removeEventListener("message", handleSocketMessage);
        };
    }, [socket]);


    return (
        <div className="game-page page">
            <div className="ChessGame widget center-page block">
                <div className="container-vertical-space-between">
                    <div className="top-bar">
                        {otherPlayers.map((player, index) => (
                            <div key={index} className={`player ${currentTurn === player.color ? "turn" : ""}`}>
                                <div className={`player-color ${player.color}`}></div>
                                <p className="name">{player.name}</p>
                                <p className="timer">{player.time}</p>
                            </div>
                        ))}
                    </div>
                    
                    < ChessGame />

                    <div className="bottom-bar">
                        <p>You are:</p>
                        <div className={`player ${currentTurn === thisPlayer.color ? "turn" : ""}`}>
                            <div className={`player-color ${thisPlayer.color}`}></div>
                            <p className="name">{thisPlayer.name}</p>
                            <p className="timer">{thisPlayer.time}</p>
                        </div>
                    </div>
                </div>
            </div>
            <div className="game-info-container widget block">   
                <div className="moves">
                    <h2>Moves:</h2>
                    <table className="move-table">
                        <tbody>
                            {moves.map((round, index) => (
                                <tr key={index}>
                                    <td>{index + 1}</td>
                                    {round.map((move, i) => (
                                        <td key={i}>{move || "-"}</td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                <div className="game-options">
                    
                </div>
            </div>
        </div>
    );
};

export default GamePage;