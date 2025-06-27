import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { API_BASE_URL } from "../../utils/ApiUrls";

import './DatabasePage.css';


const DatabasePage = () => {
    const [gameFiles, setGameFiles] = useState([]);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchGames = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/game-local/get-games`);
                if (!response.ok) throw new Error("Failed to fetch games");
                const data = await response.json();
                setGameFiles(data);
            } catch (error) {
                console.error("Error fetching games:", error);
            }
        };

        fetchGames();
    }, []);

    const loadGame = async (fileName) => {
        try {
            const response = await fetch(`${API_BASE_URL}/game-local/load-game`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ name: fileName }),
            });

            if (!response.ok) throw new Error("Failed to load game");
            const data = await response.json();

            navigate("/game-local", {
                state: {
                    gameId: data.gameId,
                    gameType: data.gameType,
                    boardSize: data.boardSize,
                    initialState: data.states,
                    playerCount: data.playerCount,
                    turnInfo: data.turn,
                    players: data.players,
                },
            });
        } catch (error) {
            console.error("Error loading game:", error);
            alert("Failed to load game.");
        }
    };

    return (
        <div className="widget page">
            <h1>Game Database</h1>

            <div className="boxes1">
                <div className="box game-setup">
                    <h3>Watch a Game</h3>
                    <ul className="game-file-list">
                        {gameFiles.map((file, index) => (
                            <li
                                key={index}
                                className="game-file-item"
                                onClick={() => loadGame(file)}
                            >
                                {file}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default DatabasePage;
