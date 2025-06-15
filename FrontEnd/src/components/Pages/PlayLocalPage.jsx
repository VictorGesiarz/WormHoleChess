import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { API_BASE_URL } from "../../utils/ApiUrls";

import "./PlayLocalPage.css";


const PlayLocalPage = () => {
    const navigate = useNavigate();

    // - - - - - - - - - - - - - - - - CONSTANTS - - - - - - - - - - - - - - - - 
    const [playerCount, setPlayerCount] = useState(4);
    const [boardSize, setBoardSize] = useState(8);
    const [gameType, setGameType] = useState('wormhole');
    const [programMode, setProgramMode] = useState('matrix');
    const [boardImage, setBoardImage] = useState('/assets/images/8x8_wormhole.png');
    const [possiblePositions, setPossiblePositions] = useState({});
    const [selectedPosition, setSelectedPosition] = useState('default');

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

    useEffect(() => {
        getPossiblePositions();
    }, []);

    // - - - - - - - - - - - - - - - - PAGE FUNCTIONS - - - - - - - - - - - - - - - - 
    const getPossiblePositions = async () => {
        const response = await fetch(`${API_BASE_URL}/game-local/get-possible-positions`, {
            method: "GET"
        });

        if (response.ok) {
            const data = await response.json();
            setPossiblePositions(data);
            setSelectedPosition(data[`${playerCount}_${boardSize}x${boardSize}_${gameType}`][0])
        } else {
            const error = await response.json();
            console.error("Failed to fetch possible positions:", error);
            alert("Failed to fetch possible positions.");
        }
    };
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
    const handleSelectedSize = (size, type) => {
        setBoardImage(`/assets/images/${size}x${size}_${type}.png`);
    }


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
                initialPosition: selectedPosition,
            }),
        });

        if (response.ok) {
            const data = await response.json();
            console.log("Redirecting to game page")
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
                            {possiblePositions[`${playerCount}_${boardSize}x${boardSize}_${gameType}`] && (
                                <select
                                    id="position-dropdown"
                                    className="dropdown"
                                    value={selectedPosition}
                                    onChange={(e) => setSelectedPosition(e.target.value)}
                                >
                                    {possiblePositions[`${playerCount}_${boardSize}x${boardSize}_${gameType}`].map((position, index) => (
                                        <option key={index} value={position}>
                                            {position}
                                        </option>
                                    ))}
                                </select>
                            )}
                        </div>

                        <div className="board-image">
                            <img src={boardImage} alt={boardImage} />
                        </div>

                        <div className="game-parameters-buttons">
                            <div className="player-toggle">
                                <button
                                    className={`toggle-option ${playerCount === 2 ? 'active' : ''}`}
                                    onClick={() => { setPlayerCount(2) }}
                                >
                                    2 Players
                                </button>
                                {gameType !== 'normal' && (<button
                                    className={`toggle-option ${playerCount === 4 ? 'active' : ''}`}
                                    onClick={() => setPlayerCount(4)}
                                >
                                    4 Players
                                </button>)}
                            </div>

                            <div className="player-toggle">
                                {gameType === 'normal' ? (
                                    [4, 5, 6, 8].map((size) => (
                                        <button
                                            key={size}
                                            className={`toggle-option small ${boardSize === size ? 'active' : ''}`}
                                            onClick={() => {
                                                setBoardSize(size);
                                                handleSelectedSize(size, 'normal');
                                            }}
                                        >
                                            {size} x {size}
                                        </button>
                                    ))
                                ) : (
                                    <>
                                        <button
                                            className={`toggle-option ${boardSize === 6 ? 'active' : ''}`}
                                            onClick={() => {
                                                setBoardSize(6);
                                                handleSelectedSize(6, 'wormhole');
                                            }}
                                        >
                                            Small (6x6)
                                        </button>
                                        <button
                                            className={`toggle-option ${boardSize === 8 ? 'active' : ''}`}
                                            onClick={() => {
                                                setBoardSize(8);
                                                handleSelectedSize(8, 'wormhole');
                                            }}
                                        >
                                            Big (8x8)
                                        </button>
                                    </>
                                )}
                            </div>

                            <div className="player-toggle">
                                <button
                                    className={`toggle-option ${gameType === 'normal' ? 'active' : ''}`}
                                    onClick={() => {
                                        setGameType('normal');
                                        setPlayerCount(2);
                                        setBoardSize(8);
                                        handleSelectedSize(8, 'normal');
                                    }}
                                >
                                    Normal
                                </button>
                                <button
                                    className={`toggle-option ${gameType === 'wormhole' ? 'active' : ''}`}
                                    onClick={() => {
                                        setGameType('wormhole');
                                        setBoardSize(8);
                                        handleSelectedSize(8, 'wormhole');
                                    }}
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
                                            {programMode === 'matrix' && (
                                                <>
                                                    <option value="mcts">mcts</option>
                                                    <option value="mcts-parallel">mcts (parallel)</option>
                                                    <option value="alphazero">alphazero</option>
                                                </>
                                            )}
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
