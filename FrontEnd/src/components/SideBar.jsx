import React from "react";
import { useNavigate } from "react-router-dom";
import "./SideBar.css";

const SideBar = () => {
    const navigate = useNavigate();

    return (
        <nav className="widget sidebar">
            <div className="sidebar-title">
                WormHoleChess
            </div>
            <ul className="sidebar-links">
                <li><button onClick={() => navigate("/")}>Home</button></li>
                <li><button onClick={() => navigate("/game")}>Game</button></li>
                <li><button onClick={() => navigate("/about")}>About</button></li>
                <li><button onClick={() => navigate("/rules")}>Rules</button></li>
                <li><button onClick={() => navigate("/pruebas")}>Pruebas</button></li>
            </ul>
        </nav>
    );
};

export default SideBar;
