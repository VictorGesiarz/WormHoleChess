import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { IoArrowBack } from "react-icons/io5"; 

import { useAuth } from "../../../utils/AuthContext";

import "./LoginPage.css";


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;


function LoginPage() {
    const { token, login } = useAuth();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();

        const formData = new URLSearchParams();
        formData.append("username", email);
        formData.append("password", password);

        try {
            const response = await fetch(`${API_BASE_URL}/auth/token`, {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Login failed");
            }

            const data = await response.json();
            login(data.access_token);
            navigate("/lobby");
        } catch (error) {
            console.error("Login error:", error);
            alert("Invalid credentials");
        }
    };

    return (
        <div className="widget box">
            {/* Back Arrow */}
            <button className="back-button" onClick={() => navigate("/")}>
                <IoArrowBack size={24} /> Back
            </button>

            <h2>Login</h2>
            <form onSubmit={handleLogin}>
                <input
                    className="input"
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <input
                    className="input"
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit" className="button">Login</button>
            </form>
            <p>
                Don't have an account? <Link to="/register">Register here</Link>
            </p>
        </div>
    );
}

export default LoginPage;
