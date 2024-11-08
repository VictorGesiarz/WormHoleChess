import React from "react";
import { useNavigate } from "react-router-dom";
import "./Navbar.css";

const Navbar = () => {
    const navigate = useNavigate(); // Works here because it's a functional component

    return (
        <nav className="navbar">
            <div className="navbar-panel">
                WormHoleChess
            </div>
            <ul className="navbar-links">
                <li><button onClick={() => navigate("/home")}>Home</button></li>
                <li><button onClick={() => navigate("/game")}>Game</button></li>
                <li><button onClick={() => navigate("/about")}>About</button></li>
                <li><button onClick={() => navigate("/rules")}>Rules</button></li>
            </ul>
        </nav>
    );
};

export default Navbar;
