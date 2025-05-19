import { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

import { decodeToken } from "../../utils/auth";
import { useAuth } from "../../utils/AuthContext";
import { useWebSocket } from "../../utils/WebSocketProvider";
import { API_BASE_URL, API_WEB_SOCKET_URL } from "../../utils/ApiUrls";
import "./LobbyPage.css";


const availableColors = ["white", "black", "blue", "red"];

const LobbyPage = () => {
    const location = useLocation();
    const { action, gameCode: incomingCode } = location.state || {};

    const { token } = useAuth();
    const { socket, connectWebSocket, disconnectWebSocket } = useWebSocket();
    const navigate = useNavigate();

    const user = decodeToken(token);
    const [gameCode, setGameCode] = useState("");
    const [players, setPlayers] = useState([]);
    const [playerColors, setPlayerColors] = useState(new Array(4).fill("None"));
    const isHost = useRef(false);


    // When redirected to this page we enter by creating or joining a lobby. 
    useEffect(() => {
        if (action === "create") {
            createLobby();
        } else if (action === "join" && incomingCode) {
            setGameCode(incomingCode);
            joinLobby(incomingCode);
        }
    }, [action, incomingCode]);

    
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


    const removeCurrentUser = () => {
        setGameCode(null);
        setPlayers([]);
        setSocket(null);
        isHost.current = false;
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

        setPlayerColors((prevPlayerColors) => {
            const requestBody = {
                colors: prevPlayerColors, // Now we are correctly accessing the latest colors
            };

            console.log(prevPlayerColors);

            fetch(`${API_BASE_URL}/lobby/start/${gameCode}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(requestBody) // Convert body to JSON
            }).then(response => {
                if (!response.ok) {
                    alert("Lobby does not exist or has expired.");
                }
            }).catch(error => console.error("Error starting game:", error));

            return prevPlayerColors; // Return the current state to avoid modifying it here
        });
    };


    const handleColorChange = (index, color) => {
        setPlayerColors((prev) => {
            const updatedColors = [...prev];
            updatedColors[index] = color === "None" ? null : color; // Remove color if "None" is selected
            return updatedColors;
        });
    };

    const getAvailableColors = (index) => {
        const selectedColors = playerColors.filter(Boolean); // Remove nulls
        return availableColors.filter((color) => color === playerColors[index] || !selectedColors.includes(color));
    };


    // Handle socket messages for the lobby. 
    useEffect(() => {
        if (!socket) return;

        const handleLobbyMessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === "auth_success") {
                console.log("Authenticated successfully!");
            } else if (data.type === "auth_failed") {
                console.error("Authentication failed!");
                disconnectWebSocket();
            } else if (data.type === "game_start") {
                navigate(`/game/${gameCode}`);
            } else if (data.type === "player_removed" || data.type === "player_joined" || data.type === "bot_added") {
                fetchLobbyPlayers(gameCode);
            } else if (data.type === "you_are_removed" || data.type === "lobby_expired") {
                removeCurrentUser();
            }
        };

        socket.addEventListener("message", handleLobbyMessage);

        return () => {
            socket.removeEventListener("message", handleLobbyMessage);
        };
    }, [socket, gameCode]);

    return (
        <div className="widget page center-page">
            <div className="lobby-box">
                <div className="lobby-info">
                    <h3>{gameCode ? <p>Lobby <strong>{gameCode}</strong></p> : "Create or join a lobby"}</h3>
                    {gameCode && (
                        <ul>
                            {players.length > 0 ? players.map((player, index) => (
                                <li key={index}>
                                    {/* Player Name */}
                                    <span>{player}</span>

                                    {/* Color Dropdown */}
                                    {isHost.current && (
                                        <select className="dropdown color-dropdown" value={playerColors[index] || "None"} onChange={(e) => handleColorChange(index, e.target.value)}>
                                            <option value="None">None</option>
                                            {getAvailableColors(index).map((color) => (
                                                <option key={color} value={color}>{color}</option>
                                            ))}
                                        </select>
                                    )}

                                    {/* Remove Player Button */}
                                    {isHost.current && index === 0 && (
                                        <div className="empty-div"></div>
                                    )}
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