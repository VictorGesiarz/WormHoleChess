import React, { useRef } from "react";
import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import "./LocalGamePage.css";


import ChessGame from "../Game/ChessGame";


const LocalGamePage = () => {

    // - - - - - - - - - - - - - - - - RETRIEVE SENT DATA - - - - - - - - - - - - - - - - 
    const location = useLocation();
    const {
        gameId,
        gameType,
        boardSize,
        initialState,
        playerCount,
        players,
        turnInfo,
    } = location.state;

    // - - - - - - - - - - - - - - - - PAGE VARIABLES - - - - - - - - - - - - - - - - 
    const topPlayers = players.slice(0, Math.floor(players.length / 2));
    const bottomPlayers = players.slice(Math.floor(players.length / 2));

    // - - - - - - - - - - - - - - - - GAME VARIABLES - - - - - - - - - - - - - - - - 
    const [currentState, setCurrentState] = useState([])
    const [turn, setTurn] = useState(turnInfo);
    const [states, setStates] = useState(initialState);
    const [history, setHistory] = useState([]);
    const watchingState = useRef(turnInfo.moveCount);

    const playerColors = playerCount === 2
        ? ['White', 'Black']
        : ['White', 'Black', 'Blue', 'Red'];


    // - - - - - - - - - - - - - - - - USE EFFECT FUNCTIONS - - - - - - - - - - - - - - - -     
    useEffect(() => {
        setCurrentState(states[turn.moveCount]);
        watchingState.current = turn.moveCount;
        console.log(watchingState.current);
    }, [turn]);


    // - - - - - - - - - - - - - - - - EVENT LISTENERS - - - - - - - - - - - - - - - 
    const updateBoardFromRef = () => {
        const index = watchingState.current;
        if (index >= 0 && index <= turn.moveCount) {
            setCurrentState(states[index]);
        }
    };
    
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'ArrowLeft') {
                watchingState.current = Math.max(0, watchingState.current - 1);
                console.log("Left", watchingState.current)
                updateBoardFromRef();
            } else if (e.key === 'ArrowRight') {
                watchingState.current = Math.min(turn.moveCount, watchingState.current + 1);
                console.log("Right", watchingState.current)
                updateBoardFromRef();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [states]);


    // - - - - - - - - - - - - - - - - FUNCTIONS - - - - - - - - - - - - - - - - 
    const undoMove = async () => {

    };

    // - - - - - - - - - - - - - - - - RENDER - - - - - - - - - - - - - - - - 
    return (
        <div className="game-page page">
            <div className="ChessGame widget center-page block">
                <div className="container-vertical-space-between">
                    <div className="bar">
                        {topPlayers.map((player, index) => (
                            <div key={index} className="player-data">
                                <div className={`player`}>
                                    <div className={`player-color ${player.color}`}></div>
                                    <p className="name">{`${player.name} (${player.type})`}</p>
                                </div>
                                <div className={`timer ${turn.turn === player.index ? "turn" : ""}`}>
                                    <p>10:00</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    <ChessGame
                        gameId={gameId}
                        gameType={gameType}
                        boardSize={boardSize}
                        state={currentState}
                        setStates={setStates}
                        turn={turn}
                        setTurn={setTurn}
                        players={players}
                        setHistory={setHistory}
                    />

                    <div className="bar">
                        {bottomPlayers.map((player, index) => (
                            <div key={index} className="player-data">
                                <div className={`player`}>
                                    <div className={`player-color ${player.color}`}></div>
                                    <p className="name">{`${player.name} (${player.type})`}</p>
                                </div>
                                <div className={`timer ${turn.turn === player.index ? "turn" : ""}`}>
                                    <p>10:00</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>


            <div className="game-info-container widget block">
                <div className="moves">
                    <h2>Moves:</h2>
                    <div className="move-table-wrapper">
                        <table className="move-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    {playerColors.map((color) => (
                                        <th key={color}>{color}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {history.map((entry, index) => {
                                    if (index % playerCount === 0) {
                                        const roundMoves = history.slice(index, index + playerCount);
                                        return (
                                            <tr key={index}>
                                                <td className="round-num">{index / playerCount + 1}</td>
                                                {roundMoves.map((m, i) => (
                                                    <td className="move-cell" key={i}>{m.move}</td>
                                                ))}
                                            </tr>
                                        );
                                    }
                                    return null;
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="game-options">
                    <button className="button leave-btn" onClick={() => {}}>Leave Game</button>
                    <button className="button undo-btn" onClick={() => {}}>Undo Move</button>
                </div>
            </div>
        </div>
    );
};

export default LocalGamePage;