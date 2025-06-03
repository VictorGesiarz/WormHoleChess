import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../utils/AuthContext";

import "./SideBar.css";


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


const SideBar = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState(null);
    const { token, logout } = useAuth(); 

    useEffect(() => {
        const fetchEmail = async () => {
            if (!token) return;
            try {
                const response = await fetch(`${API_BASE_URL}/auth/get_email`, {
                    method: "GET",
                    headers: { Authorization: `Bearer ${token}` },
                });

                if (!response.ok) {
                    throw new Error("Failed to get email");
                }

                const data = await response.json();
                setEmail(data.email);
            } catch (error) {
                console.error(error);
            }
        };

        fetchEmail();
    }, [token]); 

    return (
        <nav className="widget sidebar">
            <div className="sidebar-title">WormHoleChess</div>
            <ul className="sidebar-links">
                <li><button onClick={() => navigate("/")}>Home</button></li>
                <li><button onClick={() => navigate("/play")}>PlayOnline</button></li>
                <li><button onClick={() => navigate("/play-local")}>PlayLocal</button></li>
                <li><button onClick={() => navigate("/learn")}>Learn</button></li>
            </ul>

            <div className="sidebar-auth">
                {token ? (
                    <div className="logged-in">
                        <p>Logged in as <strong>{email || "Loading..."}</strong></p>
                        <br></br>
                        <button className="logout-btn" onClick={() => { logout(); navigate("/"); }}>Logout</button>
                    </div>
                ) : (
                    <button className="login-btn" onClick={() => navigate("/login")}>Login</button>
                )}
            </div>
        </nav>
    );
};

export default SideBar;
