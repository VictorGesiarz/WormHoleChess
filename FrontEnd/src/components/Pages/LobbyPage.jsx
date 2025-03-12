import { useState, useRef, useEffect, useContext } from "react";
import { useNavigate } from "react-router-dom";

import { decodeToken } from "../../utils/auth";
import { AuthContext } from "../../utils/AuthContext";
import "./LobbyPage.css";


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const API_WEB_SOCKET_URL = import.meta.env.VITE_WEBSOCKET_URL;


const LobbyPage = () => {
    const { token } = useContext(AuthContext);
    const navigate = useNavigate();

    const user = decodeToken(token); 
    const [gameCode, setGameCode] = useState("");
    const [players, setPlayers] = useState([]);
    const [socket, setSocket] = useState(null);
    const isHost = useRef(false);


    const createLobby = async () => {
        const response = await fetch(`${API_BASE_URL}/lobby/create`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
            alert("Failed to create lobby");
            return;
        }

        const data = await response.json();
        setGameCode(data.game_code);
        fetchLobbyPlayers(data.game_code);
        connectWebSocket(data.game_code);
        isHost.current = true;
    };


    const createBotLoby = async () => {
        const response = await fetch(`${API_BASE_URL}/lobby/create_bot`, {
            method: "POST", 
            headers: { Authorization: `Bearer ${token}` },
        });
    };


    const joinLobby = async () => {
        if (!gameCode) return alert("Enter a game code");

        const response = await fetch(`${API_BASE_URL}/lobby/join/${gameCode}`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
            alert("Failed to join lobby");
            return;
        }

        const data = await response.json();
        fetchLobbyPlayers(gameCode);
        connectWebSocket(gameCode, user.user_id);
        isHost.current = false;
    };

    
    const removePlayer = async (player) => {
        console.log("Removing player", player);
        const response = await fetch(`${API_BASE_URL}/lobby/${gameCode}/remove_player?player_name=${encodeURIComponent(player)}`, {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            }
        });
    
        if (!response.ok) {
            alert("Failed to remove player");
            return;
        }
    
        fetchLobbyPlayers(gameCode);
    };


    const fetchLobbyPlayers = async (code) => {
        const response = await fetch(`${API_BASE_URL}/lobby/${code}/players`, {
            method: "GET",
            headers: { Authorization: `Bearer ${token}` },
        });

        if (response.ok) {
            const data = await response.json();
            setPlayers(data.players);
        }
    };


    const addBot = async () => {
        const response = await fetch(`${API_BASE_URL}/lobby/${gameCode}/add_bot`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
            alert("Failed to add bot");
            return;
        }

        fetchLobbyPlayers(gameCode);
    };


    const startGame = async () => {
        // Ensure exactly 4 players are in the lobby
        if (players.length !== 4) {
            alert("You need exactly 4 players to start the game.");
            return;
        }
    
        // Step 1: Check if the lobby exists
        const lobbyResponse = await fetch(`${API_BASE_URL}/lobby/start/${gameCode}`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
        });
    
        if (!lobbyResponse.ok) {
            alert("Lobby does not exist or has expired.");
            return;
        }
    };
    

    const removeCurrentUser = () => {
        setGameCode(null);
        setPlayers([]);
        setSocket(null);
        isHost.current = false;
    };


    const connectWebSocket = (code) => {
        const ws = new WebSocket(`${API_WEB_SOCKET_URL}/${code}`);
    
        ws.onopen = () => {
            // Send authentication message with the token
            ws.send(JSON.stringify({ type: "auth", token }));
        };
    
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
    
            if (data.type === "auth_success") {
                console.log("Authenticated successfully!");
            } else if (data.type === "auth_failed") {
                console.error("Authentication failed!");
                ws.close();

            } else if (data.type === "game_start") {
                navigate(`/game/${code}`, { state: { gameCode: code } });

            } else if (data.type === "player_removed" || data.type === "player_joined" || data.type === "bot_added") {
                fetchLobbyPlayers(code);
            } else if (data.type === "you_are_removed" || data.type === "lobby_expired") {
                removeCurrentUser();
            }
        };
    
        ws.onclose = () => {
            console.log("WebSocket closed");
        };
    
        setSocket(ws);
    };


    return (
        <div className="widget page center-page">
            <div className="lobby-box">
                <div className="lobby-option left">
                    <h3>Create Lobby</h3>
                    <button onClick={createLobby} className="button">Create</button>
                    <button onClick={createBotLoby} className="button">Create Bot Lobby</button>
                </div>

                <div className="lobby-option right">
                    <h3>Join Lobby</h3>
                    <input
                        className="input"
                        type="text"
                        placeholder="Enter Game Code"
                        value={gameCode}
                        onChange={(e) => setGameCode(e.target.value)}
                    />
                    <button onClick={joinLobby} className="button">Join</button>
                </div>

                <div className="lobby-info">
                    <h3>{gameCode ? <p>Lobby <strong>{gameCode}</strong></p> : "Create or join a lobby"}</h3>
                    {gameCode && (
                        <ul>
                            {players.length > 0 ? players.map((player, index) => (
                                <li key={index}>
                                    {player}
                                    {isHost.current && index > 0 && (
                                        <button onClick={() => removePlayer(player)} className="remove-button">X</button>
                                    )}
                                </li>
                            )) : <p>No players yet</p>}
                        </ul>
                    )}
                    {gameCode && isHost.current && players.length < 4 && (
                        <button onClick={addBot} className="button">Add Bot</button>
                    )}
                    {gameCode && isHost.current && players.length === 4 && (
                        <button onClick={startGame} className="button">Start Game</button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default LobbyPage;
