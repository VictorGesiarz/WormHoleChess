import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { decodeToken } from "../../utils/auth";
import { useAuth } from "../../utils/AuthContext";
import { useWebSocket } from "../../utils/WebSocketProvider";
import { API_BASE_URL, API_WEB_SOCKET_URL } from "../../utils/ApiUrls";
import "./PlayPage.css";


const availableColors = ["white", "black", "blue", "red"];

const initialPositions = {
    small: [
        {
            id: 'classic-small',
            name: 'Classic Small',
            image: '/positions/small/classic.png'
        },
        {
            id: 'snipers',
            name: 'Snipers Only',
            image: '/positions/small/snipers.png'
        }
    ],
    big: [
        {
            id: 'classic-big',
            name: 'Classic Big',
            image: '/positions/big/classic.png'
        },
        {
            id: 'chaos',
            name: 'Chaos Mode',
            image: '/positions/big/chaos.png'
        },
        {
            id: 'mirror',
            name: 'Mirror Madness',
            image: '/positions/big/mirror.png'
        }
    ]
};


const PlayPage = () => {
    const { token } = useAuth();
    const { socket, connectWebSocket, disconnectWebSocket } = useWebSocket();
    const navigate = useNavigate();

    const user = decodeToken(token);
    
    // For redirecting to the lobby page
    const gameCodeRef = useRef();

    const handleCreate = () => {
        navigate("/lobby", { state: { action: "create" } });
    };

    const handleJoin = () => {
        const code = gameCodeRef.current.value.trim();
        if (!code) return alert("Please enter a game code");
        navigate("/lobby", { state: { action: "join", gameCode: code } });
    };

    // For searching a game
    const [playerCount, setPlayerCount] = useState(4);
    const [boardSize, setBoardSize] = useState('big');
    const [gameType, setGameType] = useState('ranked');
    const [selectedPosition, setSelectedPosition] = useState(initialPositions[boardSize][0]);


    const searchGame = async () => {

    }

    const createBotLoby = async () => {
        const response = await fetch(`${API_BASE_URL}/lobby/create_bot`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
        });
    };

    const loadGameFile = () => {
        // Trigger file upload or file dialog logic
    };


    return (
        <div className="widget page center-page">

            <div className="lobby-box">
                <div className="lobby-option online">

                    <div className="game-options">
                        <div className="position-selector">
                            <h3>Play Online</h3>

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

                        <div className="toggle-buttons">
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
                                    Small
                                </button>
                                <button
                                    className={`toggle-option ${boardSize === 'big' ? 'active' : ''}`}
                                    onClick={() => {
                                        setBoardSize('big'); 
                                        setSelectedPosition(initialPositions['big'][0]);
                                    }}>
                                    Big
                                </button>
                            </div>

                            <div className="player-toggle">
                                <button
                                    className={`toggle-option ${gameType === 'ranked' ? 'active' : ''}`}
                                    onClick={() => setGameType('ranked')}
                                >
                                    Ranked
                                </button>
                                <button
                                    className={`toggle-option ${gameType === 'casual' ? 'active' : ''}`}
                                    onClick={() => setGameType('casual')}
                                >
                                    Casual
                                </button>
                            </div>
                        </div>

                        <div className="position-preview">
                            <img src={selectedPosition.image} alt={selectedPosition.name} />
                        </div>
                    </div>

                    <button onClick={searchGame} className="button">Search Game</button>
                </div>

                <div className="lobby-option friends">
                    <h3>Personalized Game</h3>
                    <button onClick={handleCreate} className="button">Create Lobby</button>
                    <input
                        className="input"
                        type="text"
                        placeholder="Enter Game Code"
                        ref={gameCodeRef}
                    />
                    <button onClick={handleJoin} className="button">Join Lobby</button>
                </div>

                <div className="lobby-option watch">
                    <h3>Watch a Game</h3>
                    <button onClick={loadGameFile} className="button">Load Game File</button>

                    <button onClick={() => navigate("/profile")} className="button">Watch Game from Your History</button>

                    <button onClick={createBotLoby} className="button">Create Bot Game</button>

                    <button onClick={() => navigate("/bot-history")} className="button">Watch Bot Game from Database</button>
                </div>

                <div className="lobby-option create">
                    <h3>Create Personalized Board</h3>
                    <button onClick={() => { }} className="button">Go to edit board</button>
                </div>

            </div>
        </div>
    );
};

export default PlayPage;
