import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { API_BASE_URL } from "../../utils/ApiUrls";

import initialPositions from '../../assets/configs/image_positions';
import "./PlayLocalPage.css";


const PlayLocalPage = () => {
    const navigate = useNavigate();

    // - - - - - - - - - - - - - - - - CONSTANTS - - - - - - - - - - - - - - - - 
    const [playerCount, setPlayerCount] = useState(4);
    const [boardSize, setBoardSize] = useState('big');
    const [gameType, setGameType] = useState('wormhole');
    const [programMode, setProgramMode] = useState('layer');
    const [selectedPosition, setSelectedPosition] = useState(initialPositions[boardSize][0]);

    const [playerNames, setPlayerNames] = useState(
        Array.from({ length: playerCount }, (_, i) => `Player ${i + 1}`)
    );
    const [playerTypes, setPlayerTypes] = useState(
        Array(playerCount).fill("human")
    );
    const colors = playerCount === 2
        ? ["white", "black"]
        : ["white", "black", "blue", "red"];


    // - - - - - - - - - - - - - - - - USE EFFECT FUNCTIONS - - - - - - - - - - - - - - - - 
    useEffect(() => {
        setPlayerNames(Array.from({ length: playerCount }, (_, i) => `Player ${i + 1}`));
        setPlayerTypes(Array(playerCount).fill("human"));
    }, [playerCount]);


    // - - - - - - - - - - - - - - - - PAGE FUNCTIONS - - - - - - - - - - - - - - - - 
    // Helper: update a single player's type
    const handleTypeChange = (index, newType) => {
        setPlayerTypes((prev) => {
            const copy = [...prev];
            copy[index] = newType;
            return copy;
        });
    };
    const handleNameChange = (index, newName) => {
        setPlayerNames((prev) => {
            const updated = [...prev];
            updated[index] = newName;
            return updated;
        });
    };


    // - - - - - - - - - - - - - - - - FUNCTIONALITY FUNCTIONS - - - - - - - - - - - - - - - - 
    const start_game = async () => {
        const playerData = playerNames.map((name, index) => ({
            name,
            index,
            type: playerTypes[index],
            color: colors[index],
        }));

        const response = await fetch(`${API_BASE_URL}/game-local/start-local-game`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                // Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
                players: playerData,
                programMode,
                gameType,
                boardSize,
                positionId: selectedPosition.id,
            }),
        });

        if (response.ok) {
            const data = await response.json(); 
            navigate("/game-local", {
                state: {
                    gameId: data.gameId,
                    gameType,
                    boardSize,
                    initialState: data.initialState,
                    playerCount,
                    turnInfo: data.turn, 
                    players: playerData,
                }
            });
        } else {
            const error = await response.json();
            console.error("Failed to start game:", error);
            alert("Failed to start game.");
        }
    };


    return (
        <div className="widget page center-page">

            <h1>Play Local</h1>

            <div className="boxes1">

                {/* ──────────────────────────────────────────────────────────────────────────── */}

                <div className="box game-setup">

                    <div className="game-parameters">
                        <div className="initial-position-selector">
                            <h3>Game Setup</h3>

                            <label htmlFor="position-dropdown">Initial Position</label>
                            <select
                                id="position-dropdown"
                                className="dropdown"
                                value={selectedPosition.id}
                                onChange={(e) =>
                                    setSelectedPosition(initialPositions[boardSize].find(pos => pos.id === e.target.value))
                                }
                            >
                                {initialPositions[boardSize].map((position) => (
                                    <option key={position.id} value={position.id}>
                                        {position.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div className="board-image">
                            <img src={selectedPosition.image} alt={selectedPosition.name} />
                        </div>

                        <div className="game-parameters-buttons">
                            <div className="player-toggle">
                                <button
                                    className={`toggle-option ${playerCount === 2 ? 'active' : ''}`}
                                    onClick={() => setPlayerCount(2)}
                                >
                                    2 Players
                                </button>
                                <button
                                    className={`toggle-option ${playerCount === 4 ? 'active' : ''}`}
                                    onClick={() => setPlayerCount(4)}
                                >
                                    4 Players
                                </button>
                            </div>

                            <div className="player-toggle">
                                <button
                                    className={`toggle-option ${boardSize === 'small' ? 'active' : ''}`}
                                    onClick={() => {
                                        setBoardSize('small');
                                        setSelectedPosition(initialPositions['small'][0]);
                                    }}>
                                    Small (6x6)
                                </button>
                                <button
                                    className={`toggle-option ${boardSize === 'big' ? 'active' : ''}`}
                                    onClick={() => {
                                        setBoardSize('big');
                                        setSelectedPosition(initialPositions['big'][0]);
                                    }}>
                                    Big (8x8)
                                </button>
                            </div>

                            <div className="player-toggle">
                                <button
                                    className={`toggle-option ${gameType === 'normal' ? 'active' : ''}`}
                                    onClick={() => setGameType('normal')}
                                >
                                    Normal
                                </button>
                                <button
                                    className={`toggle-option ${gameType === 'wormhole' ? 'active' : ''}`}
                                    onClick={() => setGameType('wormhole')}
                                >
                                    Wormhole
                                </button>
                            </div>

                            <div className="player-toggle">
                                <button
                                    className={`toggle-option ${programMode === 'matrix' ? 'active' : ''}`}
                                    onClick={() => setProgramMode('matrix')}
                                >
                                    Matrix
                                </button>
                                <button
                                    className={`toggle-option ${programMode === 'layer' ? 'active' : ''}`}
                                    onClick={() => setProgramMode('layer')}
                                >
                                    Layer
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* ──────────────────────────────────────────────────────────────────────────── */}

                <div className="box players">
                    <h3>Players</h3>

                    {/* Render a simple table with exactly playerCount rows */}
                    <table className="player-table">
                        <thead>
                            <tr>
                                <th>Player</th>
                                <th>Type</th>
                                <th>Color</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Array.from({ length: playerCount }).map((_, idx) => (
                                <tr key={idx}>
                                    {/* Column 1: auto‐generated name */}
                                    <td>
                                        <input
                                            type="text"
                                            value={playerNames[idx] ?? ""}
                                            onChange={(e) => handleNameChange(idx, e.target.value)}
                                            className="player-name-input"
                                        />
                                    </td>

                                    {/* Column 2: type dropdown */}
                                    <td>
                                        <select
                                            className="dropdown type-dropdown"
                                            value={playerTypes[idx] ?? "human"}
                                            onChange={(e) =>
                                                handleTypeChange(idx, e.target.value)
                                            }
                                        >
                                            <option value="human">human</option>
                                            <option value="random">random</option>
                                            <option value="mcts">mcts</option>
                                            <option value="alphazero">alphazero</option>
                                        </select>
                                    </td>

                                    {/* Column 3: fixed color */}
                                    <td>{colors[idx]}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                </div>

                {/* ──────────────────────────────────────────────────────────────────────────── */}

                <button onClick={start_game} className="start-button button">
                    Start Game
                </button>

            </div>
        </div>
    );
};

export default PlayLocalPage;
