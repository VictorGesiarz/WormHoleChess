import React, { } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

import { AuthProvider, useAuth } from "./utils/AuthContext";
import { WebSocketProvider } from "./utils/WebSocketProvider";

import SideBar from "./components/SideBar";
import LoginPage from "./components/Pages/Authentication/LoginPage";
import RegisterPage from "./components/Pages/Authentication/RegisterPage";
import MainPage from "./components/Pages/MainPage";
import LearnPage from "./components/Pages/LearnPage";
import PlayPage from "./components/Pages/PlayPage";
import PlayLocalPage from "./components/Pages/PlayLocalPage";
import LobbyPage from "./components/Pages/LobbyPage";
import BotHistoryPage from "./components/Pages/BotHistoryPage"; 
import GamePage from "./components/Pages/GamePage";


const PrivateRoute = ({ children }) => {
    const { isAuthenticated } = useAuth();
    return isAuthenticated ? children : <Navigate to="/login" />;
};

// Layout for pages with Sidebar
const MainLayout = ({ children }) => {
    const { token, logout } = useAuth(); 
    return (
        <div className="container">
            <SideBar token={token} logout={logout} />
            <div className="content">{children}</div>
        </div>
    );
};

// Layout for authentication pages (e.g., login, register)
const AuthLayout = ({ children }) => {
    return <div className="auth-container">{children}</div>;
};

function App() {
    return (
        <AuthProvider>
            <WebSocketProvider>
                <Router>
                    <Routes>
                        {/* Authentication Routes */}
                        <Route path="/login" element={<AuthLayout><LoginPage /></AuthLayout>} />
                        <Route path="/register" element={<AuthLayout><RegisterPage /></AuthLayout>} />

                        {/* Public Pages */}
                        <Route path="/" element={<MainLayout><MainPage /></MainLayout>} />
                        <Route path="/learn" element={<MainLayout><LearnPage /></MainLayout>} />

                        {/* Protected Routes */}
                        <Route path="/play" element={<PrivateRoute><MainLayout><PlayPage /></MainLayout></PrivateRoute>} />
                        <Route path="/play" element={<MainLayout><PlayLocalPage /></MainLayout>} />
                        <Route path="/lobby" element={<PrivateRoute><MainLayout><LobbyPage /></MainLayout></PrivateRoute>} />
                        <Route path="/bot-history" element={<PrivateRoute><MainLayout><BotHistoryPage /></MainLayout></PrivateRoute>} />
                        <Route path="/game/:gameCode" element={<PrivateRoute><MainLayout><GamePage /></MainLayout></PrivateRoute>} />
                    </Routes>
                </Router>
            </WebSocketProvider>
        </AuthProvider>
    );
}

export default App;
